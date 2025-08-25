import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

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