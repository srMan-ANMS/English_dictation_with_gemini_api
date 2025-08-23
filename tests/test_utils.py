from utils import extract_video_id_from_url

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
