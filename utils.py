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

        # Gemini AI에게 역할을 부여하고 원하는 결과물의 형식을 지정하는 프롬프트입니다.
        # Spring에서 외부 API로 보낼 요청(Request) DTO를 만드는 과정과 유사하다고 볼 수 있습니다.
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
        # 외부 API를 호출하는 부분입니다. Java의 'restTemplate.postForObject()'나 Feign Client의 메소드 호출과 같습니다.
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # API 응답(response)에서 텍스트 부분만 추출하고, 불필요한 마크다운 형식을 제거합니다.
        json_response_text = response.text.strip()
        if json_response_text.startswith("```json"):
            json_response_text = (
                json_response_text.strip("```json").strip("```").strip()
            )
        
        # JSON 문자열을 Python 딕셔너리로 파싱합니다. Java의 'objectMapper.readValue(jsonString, Map.class)'와 유사합니다.
        scoring_result = json.loads(json_response_text)
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


# '@st.cache_data'는 Streamlit의 데코레이터(Decorator)입니다.
# Java/Spring 관점:
# - 이 데코레이터는 Spring의 '@Cacheable' 어노테이션과 매우 유사한 역할을 합니다.
# - 함수가 동일한 입력 인자(video_id)로 다시 호출될 때, 실제 함수를 실행하지 않고 이전에 계산된 결과를 즉시 반환합니다.
# - 이를 통해 불필요한 API 호출을 줄여 성능을 향상시킵니다.
@st.cache_data
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
        # 사용 가능한 자막 목록을 순회하며 가장 적합한 자막을 찾습니다.
        for transcript in transcript_list:
            if (
                transcript.language_code.startswith("en")
                and not transcript.is_generated
            ):
                manual_english_transcript = transcript
                st.success("✅ 수동(공식) 영어 자막을 찾았습니다!")
                break  # 가장 좋은 것을 찾았으므로 반복을 중단합니다.
            elif transcript.language_code.startswith("en"):
                generated_english_transcript = transcript

        final_transcript = None
        if manual_english_transcript:
            st.info("최종 선택: 수동 자막")
            final_transcript = manual_english_transcript
        elif generated_english_transcript:
            st.info("최종 선택: 자동 생성 자막")
            final_transcript = generated_english_transcript
        else:
            # Java에서 'throw new Exception(...)'과 같이 예외를 발생시킵니다.
            raise Exception("이 영상에는 영어 자막이 존재하지 않습니다.")

        # 선택된 자막의 전체 텍스트 데이터를 가져옵니다.
        full_transcript_data = final_transcript.fetch()
        # 자막 데이터를 하나의 긴 문자열로 합칩니다.
        # Python의 리스트 컴프리헨션(List Comprehension)으로, Java의 Stream API와 유사합니다.
        # e.g., 'fullTranscriptData.stream().map(item -> item.getText()).collect(Collectors.joining(" "))'
        full_transcript = " ".join([item.text for item in full_transcript_data])
        return full_transcript

    except Exception as e:
        st.error(f"스크립트를 가져오는 데 실패했습니다: {e}")
        return None


def clean_script(script):
    """
    정규 표현식을 사용하여 대괄호([])로 묶인 모든 문자열을 제거하고 공백을 정돈합니다.

    Java/Spring 관점:
    - 're.sub()' 함수는 Java의 'String.replaceAll()' 메소드와 기능적으로 동일합니다.
    - 정규 표현식을 사용하여 문자열의 특정 패턴을 찾아 다른 문자열로 대체합니다.
    """
    # r'\['.*?\].' 패턴: '['로 시작해서 ']'로 끝나는 모든 문자열을 찾습니다.
    cleaned_script = re.sub(r"\[.*?\]", "", script)
    # 줄바꿈 문자를 공백으로 바꿉니다.
    cleaned_script = cleaned_script.replace("\n", " ")
    # 여러 개의 공백을 하나로 합칩니다.
    cleaned_script = " ".join(cleaned_script.split())
    return cleaned_script


def split_into_sentences(script):
    """
    스크립트를 문장 단위로 나눕니다.

    Java/Spring 관점:
    - 're.split()' 함수는 Java의 'String.split()' 메소드와 유사하지만, 정규 표현식을 사용하여 더 복잡한 구분자로 분리할 수 있습니다.
    """
    # 정규 표현식 설명:
    # '(?<=[.?!])'는 '후방 탐색(lookbehind)' 구문으로, . ? ! 문자가 바로 뒤에 오는 위치를 찾되, 그 문자 자체는 결과에 포함시키지 않습니다.
    # '\s+'는 하나 이상의 공백 문자를 의미합니다.
    # 즉, 문장 부호(.?!) 뒤에 공백이 오는 지점을 기준으로 문자열을 나눕니다.
    sentences = re.split(r"(?<=[.?!])\s+", script)
    # 리스트 컴프리헨션을 사용하여 분리된 각 문장의 양쪽 공백을 제거하고, 빈 문자열은 리스트에서 제외합니다.
    # Java Stream: 'Arrays.stream(sentences).map(String::trim).filter(s -> !s.isEmpty()).collect(Collectors.toList())'
    return [s.strip() for s in sentences if s.strip()]