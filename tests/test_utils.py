from utils import extract_video_id_from_url
from youtube_script_processor import clean_script, split_into_sentences

# 테스트 함수의 이름은 'test_'로 시작해야 pytest가 인식합니다.


def test_extract_video_id_from_standard_url():
    """일반적인 watch?v= 형태의 URL을 테스트합니다."""
    url = "https://www.youtube.com/watch?v=M-y14-3Y6gE"
    expected_id = "M-y14-3Y6gE"
    # assert는 Java의 assert와 동일합니다. 결과가 참이 아니면 테스트는 실패합니다.
    assert extract_video_id_from_url(url) == expected_id


def test_extract_video_id_from_short_url():
    """짧은 youtu.be/ 형태의 URL을 테스트합니다."""
    url = "https://youtu.be/M-y14-3Y6gE"
    expected_id = "M-y14-3Y6gE"
    assert extract_video_id_from_url(url) == expected_id


def test_extract_video_id_from_invalid_url():
    """유효하지 않은 URL을 테스트합니다."""
    url = "https://www.google.com"
    # 유효하지 않은 URL의 경우 None을 반환해야 합니다.
    assert extract_video_id_from_url(url) is None


def test_extract_video_id_with_additional_params():
    """다른 파라미터가 포함된 URL을 테스트합니다."""
    url = "https://www.youtube.com/watch?v=M-y14-3Y6gE&t=120s"
    expected_id = "M-y14-3Y6gE"
    assert extract_video_id_from_url(url) == expected_id

# --- clean_script 함수 테스트 --- 


def test_clean_script_removes_brackets():
    """대괄호([])로 묶인 내용을 제거하는지 테스트합니다."""
    script = "This is a test [with some noise] that should be removed."
    expected = "This is a test that should be removed."
    assert clean_script(script) == expected


def test_clean_script_handles_newlines():
    """개행문자(\n)를 공백으로 변환하는지 테스트합니다."""
    script = "First line.\nSecond line."
    expected = "First line. Second line."
    assert clean_script(script) == expected


def test_clean_script_normalizes_spaces():
    """여러 개의 공백을 하나로 합치는지 테스트합니다."""
    script = "This  script   has    extra spaces."
    expected = "This script has extra spaces."
    assert clean_script(script) == expected


def test_clean_script_with_no_special_chars():
    """정리할 문자가 없는 경우 원본을 유지하는지 테스트합니다."""
    script = "This is a clean sentence."
    expected = "This is a clean sentence."
    assert clean_script(script) == expected


# --- split_into_sentences 함수 테스트 --- 


def test_split_into_sentences_basic():
    """기본적인 문장 분리가 잘 되는지 테스트합니다."""
    script = "Hello world. This is a test! Is it working?"
    expected = ["Hello world.", "This is a test!", "Is it working?"]
    assert split_into_sentences(script) == expected


def test_split_into_sentences_with_extra_spaces():
    """구두점 뒤에 여러 공백이 있는 경우를 테스트합니다."""
    script = "First sentence.  Second sentence?   Third sentence!"
    expected = ["First sentence.", "Second sentence?", "Third sentence!"]
    assert split_into_sentences(script) == expected


def test_split_into_sentences_no_punctuation():
    """구두점이 없는 경우 하나의 문장으로 처리하는지 테스트합니다."""
    script = "This is just one long sentence without any punctuation"
    expected = ["This is just one long sentence without any punctuation"]
    assert split_into_sentences(script) == expected


def test_split_into_sentences_empty_string():
    """빈 문자열을 입력했을 때 빈 리스트를 반환하는지 테스트합니다."""
    script = ""
    expected = []
    assert split_into_sentences(script) == expected

from utils import evaluate
import pytest
from unittest.mock import patch, MagicMock, mock_open

# --- evaluate 함수 테스트 --- 

@patch('utils.genai.Client')
def test_evaluate_loads_prompt_from_file(mock_gemini_client):
    """
    evaluate 함수가 파일에서 프롬프트 템플릿을 올바르게 로드하는지 테스트합니다.
    Java/Spring 관점:
    - @patch는 Spring의 @MockBean과 유사합니다. 실제 객체 대신 모의(mock) 객체를 주입하여
      외부 서비스(Gemini API) 호출 없이 순수하게 내부 로직만을 테스트할 수 있게 합니다.
    """
    # 모의(mock) 클라이언트와 응답 객체를 설정합니다.
    # 실제 API 응답을 흉내 내어, API 호출이 성공했다고 가정합니다.
    mock_response = MagicMock()
    mock_response.text = '{"score": 100, "positive_feedback": "Great job!", "points_for_improvement": []}'
    mock_gemini_client.return_value.models.generate_content.return_value = mock_response

    # 테스트용 프롬프트 파일 내용을 정의합니다.
    mock_prompt_content = "Prompt template: {original_text} vs {user_text}"

    # 'builtins.open'을 모킹하여 실제 파일 I/O를 방지합니다.
    # mock_open()은 파일 읽기 작업을 가로채 미리 정의된 내용을 반환합니다.
    # Spring에서 테스트 시 파일 시스템 대신 인메모리 데이터베이스나 리소스를 사용하는 것과 유사한 원리입니다.
    with patch('builtins.open', mock_open(read_data=mock_prompt_content)) as mock_file:
        # 테스트할 함수를 호출합니다.
        evaluate("original", "user")

        # open 함수가 올바른 경로로 호출되었는지 확인합니다.
        mock_file.assert_called_once_with("prompts/evaluation_prompt.md", "r", encoding="utf-8")

        # Gemini API 클라이언트의 generate_content 메소드가 호출될 때,
        # 파일에서 읽은 내용으로 포맷팅된 프롬프트가 전달되었는지 확인합니다.
        expected_prompt = mock_prompt_content.format(original_text="original", user_text="user")
        mock_gemini_client.return_value.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents=expected_prompt
        )
