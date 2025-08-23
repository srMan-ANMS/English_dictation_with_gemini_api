import re
import json
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from google import genai

def evaluate(original_text, user_text):
    """
    사용자가 얼마나 원본 텍스트를 잘 받아쓰기했는지 Gemini API를 사용하여 평가합니다.
    성공 시 평가 결과를 담은 JSON 객체를, 실패 시 오류 정보를 담은 JSON 객체를 반환합니다.
    """
    try:
        client = genai.Client() # 환경 변수 GEMINI_API_KEY를 자동으로 사용합니다.

        # 채점을 위한 프롬프트 작성 (JSON 형식 요청 포함)
        prompt = f"""
You are a helpful and friendly English teacher. Please compare the 'Original Script' with the 'Student's Dictation' below and grade it.

Grading Criteria:
1. Accuracy (typos, missing words, extra words)
2. Grammar and punctuation

You MUST return the result in the following JSON format:
{{
  "score": <an integer score between 0 and 100>,
  "positive_feedback": "<A positive feedback on what the student did well>",
  "points_for_improvement": [
    {{
      "original": "<The original sentence or phrase>",
      "user_input": "<What the student wrote>",
      "suggestion": "<A suggestion for improvement or an explanation>"
    }}
  ]
}}

---
**[Original Script]**
{original_text}

**[Student's Dictation]**
{user_text}
---
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        json_response_text = response.text.strip()
        if json_response_text.startswith("```json"):
            json_response_text = json_response_text.strip("```json").strip("```").strip()

        scoring_result = json.loads(json_response_text)
        return scoring_result

    except json.JSONDecodeError as e:
        # JSON 파싱 오류 시, 오류 정보와 원본 응답을 함께 반환
        return {
            "error": "JSON 파싱 오류",
            "details": str(e),
            "raw_response": response.text if 'response' in locals() else "응답 객체를 받지 못했습니다."
        }
    except Exception as e:
        # 기타 오류 발생 시, 오류 정보를 반환
        return {
            "error": "기타 오류",
            "details": str(e),
            "raw_response": "해당 오류 유형에서는 원본 응답을 사용할 수 없습니다."
        }


# ✨ 새로운 함수 추가: 유튜브 URL에서 영상 ID 추출
def extract_video_id_from_url(url):
    """
    유튜브 URL에서 영상 ID를 추출합니다.
    다양한 URL 형식 (watch, youtu.be)을 처리합니다.
    """
    parsed_url = urlparse(url)

    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        # 일반적인 youtube.com/watch?v= 형식
        query_params = parse_qs(parsed_url.query)
        if 'v' in query_params:
            return query_params['v'][0]
    elif parsed_url.hostname == 'youtu.be':
        # 짧은 youtu.be/ 형식
        return parsed_url.path[1:] # /를 제외한 나머지 경로가 ID
    
    return None # 유효한 유튜브 ID를 찾지 못한 경우

def get_youtube_transcript(video_id):
    """
    유튜브 영상 ID로 스크립트를 가져오는 함수.
    1. 수동(공식) 영어 자막을 최우선으로 찾습니다.
    2. 없을 경우, 자동 생성 영어 자막을 찾습니다.
    """
    try:
        api = YouTubeTranscriptApi() 
        transcript_list = api.list(video_id)

        manual_english_transcript = None
        generated_english_transcript = None

        st.info("자막 목록을 검색합니다... (잠시만 기다려주세요)") 
        for transcript in transcript_list:
            if transcript.language_code.startswith('en') and not transcript.is_generated:
                manual_english_transcript = transcript
                st.success("✅ 수동(공식) 영어 자막을 찾았습니다!") 
                break  
            elif transcript.language_code.startswith('en'):
                generated_english_transcript = transcript
        
        final_transcript = None
        if manual_english_transcript:
            st.info("최종 선택: 수동 자막") 
            final_transcript = manual_english_transcript
        elif generated_english_transcript:
            st.info("최종 선택: 자동 생성 자막") 
            final_transcript = generated_english_transcript
        else:
            raise Exception("이 영상에는 영어 자막이 존재하지 않습니다.")

        full_transcript_data = final_transcript.fetch()
        full_transcript = " ".join([item.text for item in full_transcript_data])
        return full_transcript

    except Exception as e:
        st.error(f"스크립트를 가져오는 데 실패했습니다: {e}") 
        return None

def clean_script(script):
    """
    정규 표현식을 사용하여 대괄호([])로 묶인 모든 문자열을 제거하고 공백을 정돈합니다.
    """
    cleaned_script = re.sub(r'[[.*?]]', '', script)
    cleaned_script = cleaned_script.replace('\n', ' ')
    cleaned_script = ' '.join(cleaned_script.split())
    return cleaned_script

def split_into_sentences(script):
    """
    스크립트를 문장 단위로 나눕니다.
    """
    # . ? ! 뒤에 공백이 오는 경우를 기준으로 문장을 나눕니다.
    sentences = re.split(r'(?<=[.?!])\s+', script)
    # 빈 문자열이 리스트에 포함되는 것을 방지합니다.
    return [s.strip() for s in sentences if s.strip()]
