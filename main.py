import streamlit as st

from utils import (
    extract_video_id_from_url,
    get_youtube_transcript,
    clean_script,
    evaluate,
    split_into_sentences,
)

if __name__ == "__main__":
    st.set_page_config(page_title="YouTube 받아쓰기 앱", layout="centered")
    st.title("📚 YouTube 영어 받아쓰기 앱")

    st.write(
        "유튜브 영상의 스크립트를 가져와 문장 단위로 받아쓰기 연습을 할 수 있습니다."
    )

    youtube_url = st.text_input(
        "유튜브 영상 URL을 입력하세요:",
        help="예: https://www.youtube.com/watch?v=M-y14-3Y6gE",
    )

    # --- Session State 초기화 --- #
    if "sentences" not in st.session_state:
        st.session_state.sentences = []
        st.session_state.total_sentences = 0
        st.session_state.current_sentence_index = 0
        st.session_state.user_inputs = []
        st.session_state.scores = []

    if st.button("스크립트 가져오기", key="get_script_button"):
        if youtube_url:
            video_id = extract_video_id_from_url(youtube_url)
            if video_id:
                with st.spinner("스크립트를 처리 중입니다..."):
                    original_script = get_youtube_transcript(video_id)

                if original_script:
                    refined_script = clean_script(original_script)
                    sentences = split_into_sentences(refined_script)

                    st.session_state.sentences = sentences
                    st.session_state.total_sentences = len(sentences)
                    st.session_state.current_sentence_index = 0
                    st.session_state.user_inputs = ["" for _ in sentences]
                    st.session_state.scores = [None for _ in sentences]
                    st.success(
                        f"총 {st.session_state.total_sentences}개의 문장을 찾았습니다. 받아쓰기를 시작하세요!"
                    )
                else:
                    st.warning(
                        "영상의 스크립트를 가져오는 데 실패했습니다. URL을 확인하거나 다른 영상을 시도해주세요."
                    )
            else:
                st.error("유효한 유튜브 영상 URL이 아닙니다. 다시 확인해주세요.")
        else:
            st.warning("유튜브 영상 URL을 입력해주세요.")

    # --- 받아쓰기 인터페이스 --- #
    if st.session_state.sentences:
        st.markdown("---")

        # 현재 문장 정보 표시
        idx = st.session_state.current_sentence_index
        total = st.session_state.total_sentences
        st.write(f"**문장 {idx + 1} / {total}**")

        st.subheader("✅ 원본 스크립트")
        st.write(st.session_state.sentences[idx])

        st.subheader("✍️ 당신의 받아쓰기")
        user_input = st.text_area(
            "영상을 듣고 받아쓰기한 내용을 여기에 입력하세요:",
            value=st.session_state.user_inputs[idx],
            key=f"user_input_{idx}",  # 각 문장마다 고유한 키 부여
        )
        st.session_state.user_inputs[idx] = user_input

        # --- 네비게이션 및 채점 버튼 --- #
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

        with col1:
            if st.button("이전", disabled=(idx <= 0)):
                st.session_state.current_sentence_index -= 1
                st.rerun()

        with col2:
            if st.button("채점하기", use_container_width=True):
                if user_input:
                    with st.spinner("Gemini AI가 채점 중입니다..."):
                        scoring_result = evaluate(
                            st.session_state.sentences[idx], user_input
                        )
                        st.session_state.scores[idx] = scoring_result
                else:
                    st.warning("받아쓰기 내용을 입력해주세요!")

        with col3:
            # 전체 진행률 표시 버튼 (새로운 기능)
            # 이 버튼을 누르면 전체 문장에 대한 점수 요약을 보여줄 수 있습니다.
            # 지금은 비워둡니다.
            pass

        with col4:
            if st.button("다음", disabled=(idx >= total - 1)):
                st.session_state.current_sentence_index += 1
                st.rerun()

        # --- 채점 결과 표시 --- #
        if st.session_state.scores[idx]:
            with st.expander("채점 결과 보기", expanded=True):
                scoring_results = st.session_state.scores[idx]

                # 오류가 있는지 확인하고, 있으면 상세 정보 표시
                if "error" in scoring_results:
                    st.error(f"채점 중 오류 발생: {scoring_results.get('error')}")
                    st.text(f"오류 상세 내용: {scoring_results.get('details')}")
                    st.subheader("Gemini AI 원본 응답:")
                    st.code(scoring_results.get("raw_response"))
                else:
                    # 기존의 성공적인 결과 표시
                    st.write(f"**💯 총점:** {scoring_results.get('score')}/100")
                    st.write(
                        f"**👍 잘한 점:** {scoring_results.get('positive_feedback')}"
                    )

                    points = scoring_results.get("points_for_improvement", [])
                    if points:
                        st.write("**✏️ 개선할 점:**")
                        for point in points:
                            st.markdown(f"- **원본:** `{point.get('original')}`")
                            st.markdown(f"  **입력:** `{point.get('user_input')}`")
                            st.markdown(f"  **제안:** {point.get('suggestion')}\n")
                    else:
                        st.info("훌륭합니다! 특별히 개선할 점이 보이지 않습니다.")

    st.markdown("---")
    st.info("이 앱은 Gemini AI와 YouTube Transcript API를 사용하여 만들어졌습니다.")
