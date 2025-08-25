from utils import extract_video_id_from_url, clean_script, split_into_sentences

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