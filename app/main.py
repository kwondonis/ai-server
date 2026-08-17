from fastapi import FastAPI, HTTPException
from app.schemas.chat import ChatRequest
from app.core.prompts import COACH_PREAMBLE
import cohere
import json
import os
from dotenv import load_dotenv

# .env 파일에서 비밀키 불러오기
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY 환경변수가 설정되지 않았습니다.")

co = cohere.Client(COHERE_API_KEY)

app = FastAPI(title="Pillter AI Server")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        current_supps = ", ".join(request.user_profile.current_supplements) if request.user_profile.current_supplements else "없음"
        
        # 동적 추천 질문 생성을 포함한 메인 프롬프트 조립
        prompt = f"""
        [회원 신체 정보]
        나이: {request.user_profile.age}세, 성별: {request.user_profile.gender}, 키: {request.user_profile.height}cm, 몸무게: {request.user_profile.weight}kg
        현재 복용 중인 영양제: {current_supps}
        
        [DB 추천 정보]
        {request.db_context if request.db_context else "조건에 맞는 제품 없음."}
        
        [회원의 질문]
        {request.user_message}

        위 정보를 바탕으로 이민재 코치의 페르소나로 답변을 작성해.
        
        답변이 끝난 후, 이 회원이 이어서 물어볼 만한 '추천 질문' 3가지를 생성해.
        반드시 아래의 JSON 형식으로만 응답해야 해:
        {{
            "reply": "여기에 코치의 답변",
            "suggested_questions": ["질문1", "질문2", "질문3"]
        }}
        """

        # Command R 모델 호출
        response = co.chat(
            model="command-a-03-2025",
            preamble=COACH_PREAMBLE,
            message=prompt,
            chat_history=request.chat_history,
            temperature=0.7
        )

        # 텍스트 형태의 응답을 JSON으로 변환
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        result_data = json.loads(raw_text)

        return {
            "status": "success",
            "data": result_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 폴더 구조가 바뀌었으므로 실행 경로를 명시합니다.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)