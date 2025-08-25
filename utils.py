# Java/Spring 관점에서의 설명:
# 이 'utils.py' 파일은 Java 프로젝트의 'util' 패키지나 특정 도메인 서비스 클래스와 유사한 역할을 합니다.
# 애플리케이션의 여러 부분에서 공통적으로 사용될 수 있는 헬퍼(helper) 함수나 비즈니스 로직을 모아둡니다.
# 예를 들어, 'YoutubeService'나 'GeminiApiService' 클래스에 있을 법한 메소드들이 여기에 함수 형태로 존재합니다.

import re
import json
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from google import genai
from pydantic import BaseModel # 모델이 JSON을 생성하도록 제한하기 위해 Recipe 클래스에서 필요해서


def evaluate(original_text, user_text):
    """
    사용자가 얼마나 원본 텍스트를 잘 받아쓰기했는지 Gemini API를 사용하여 평가합니다.
    성공 시 평가 결과를 담은 JSON 객체를, 실패 시 오류 정보를 담은 JSON 객체를 반환합니다.

    Java/Spring 관점:
    - 이 함수는 외부 API(Gemini)를 호출하는 서비스 메소드(e.g., 'evaluateDictation')와 같습니다.
    - 'try...except' 블록은 Java의 'try...catch'와 동일하며, 예외 처리를 담당합니다.
    - 'json.loads()'는 JSON 문자열을 Python 객체(딕셔너리)로 변환하는 기능으로, Java의 Jackson이나 Gson 라이브러리가 JSON을 DTO 객체로 변환하는 것과 유사합니다.
    """
    try:
        # Java의 'new GeminiApiClient()'와 같이 클라이언트 객체를 생성합니다.
        # API 키는 환경 변수에서 자동으로 로드됩니다. Spring의 @Value("${gemini.api.key}")와 유사한 방식입니다.
        client = genai.Client()

        # https://ai.google.dev/gemini-api/docs/structured-output?hl=ko에서 가져옴
        # 모델이 JSON 파일로만 응답하도록 responseSchema를 구성함.
        class Recipe(BaseModel):
            recipe_name: str
            ingredients: list[str]

        # Java에서 설정 파일을 읽어오듯, .md 파일에서 프롬프트 템플릿을 읽어옵니다.
        # 이는 Spring의 ResourceLoader를 사용하여 클래스패스나 파일 시스템에서 리소스를 읽는 것과 유사합니다.
        with open("prompts/evaluation_prompt.md", "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # 읽어온 템플릿에 실제 값을 채워넣어 최종 프롬프트를 완성합니다.
        # Java의 String.format()이나 메시지 템플릿을 사용하는 것과 같습니다.
        prompt = prompt_template.format(
            original_text=original_text, user_text=user_text
        )
        # 외부 API를 호출하는 부분입니다. Java의 'restTemplate.postForObject()'나 Feign Client의 메소드 호출과 같습니다.
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Recipe],
            },
        )

        # test부분. 나중에 완료되면 삭제할 것
        print("response.text: " + response.text)

        # # API 응답(response)에서 텍스트 부분만 추출하고, 불필요한 마크다운 형식을 제거합니다.
        # 250825:1638: 어차피 API에 JSON 주라 했으니까 불필요한 부분임.
        # json_response_text = response.text.strip()
        # if json_response_text.startswith("```json"):
        #     json_response_text = (
        #         json_response_text.strip("```json").strip("```").strip()
        #     )

        # print("json_response_text : " + json_response_text)
        
        # JSON 문자열을 Python 딕셔너리로 파싱합니다. Java의 'objectMapper.readValue(jsonString, Map.class)'와 유사합니다.
        scoring_result = json.loads(response.text)  # 위의 코드가 있다면 response.text는 json_response_text임.
        return scoring_result

    except json.JSONDecodeError as e:
        # Java의 'catch (JsonProcessingException e)'와 유사합니다. JSON 파싱 실패 시 예외를 처리합니다.
        return {
            "error": "JSON 파싱 오류",
            "details": str(e),
            "raw_response": response.text
            if "response" in locals() else "응답 객체를 받지 못했습니다.",
        }
    except Exception as e:
        # Java의 'catch (Exception e)'와 같이, 예상치 못한 모든 예외를 처리하는 부분입니다.
        return {
            "error": "기타 오류",
            "details": str(e),
            "raw_response": "해당 오류 유형에서는 원본 응답을 사용할 수 없습니다.",
        }


def extract_video_id_from_url(url):
    """
    유튜브 URL에서 영상 ID를 추출합니다. 다양한 URL 형식 (watch, youtu.be)을 처리합니다.

    Java/Spring 관점:
    - Java의 'java.net.URL' 클래스나 Apache Commons 'URIBuilder'를 사용하여 URL을 파싱하고 쿼리 파라미터를 추출하는 것과 동일한 로직입니다.
    - 순수한 로직만 담고 있는 유틸리티 메소드(e.g., 'UrlUtils.extractVideoId(url)')와 같습니다.
    """
    # 'urllib.parse'는 Python의 표준 라이브러리로, URL을 구성요소(scheme, netloc, path 등)로 분해하는 기능을 제공합니다.
    parsed_url = urlparse(url)

    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        # 쿼리 문자열을 파싱하여 딕셔너리 형태로 만듭니다. e.g., 'v=M-y14-3Y6gE' -> {'v': ['M-y14-3Y6gE']}
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]
    elif parsed_url.hostname == "youtu.be":
        # 'youtu.be/' 다음의 경로가 비디오 ID입니다.
        return parsed_url.path[1:]

    return None
