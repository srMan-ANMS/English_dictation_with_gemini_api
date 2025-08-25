# Java/Spring 관점에서의 설명:
# 이 'main.py' 파일은 Spring Boot 애플리케이션의 메인 클래스(@SpringBootApplication 어노테이션이 붙은 클래스)와 유사한 역할을 합니다.
# 'streamlit run main.py' 명령어로 실행될 때, 이 파일이 전체 웹 애플리케이션의 시작점이자 UI 렌더링 로직을 담고 있는 곳입니다.
# Streamlit은 코드를 위에서 아래로 순차적으로 실행하여 UI를 그립니다. 사용자 인터랙션이 발생하면 스크립트 전체가 다시 실행됩니다.

import streamlit as st

# 'from utils import ...'는 Java의 'import com.example.project.utils.YoutubeUtils;'와 같이
# 다른 파일(모듈)에 정의된 함수들을 가져오는 구문입니다.
from utils import (
    extract_video_id_from_url,  
    evaluate,    
)

from youtube_script_processor import (
    get_youtube_transcript,
    clean_script,
    split_into_sentences
)

# 'if __name__ == "__main__":' 블록은 이 스크립트 파일이 직접 실행될 때만 내부 코드를 실행하도록 하는 Python의 관용구입니다.
# Java의 'public static void main(String[] args)' 메소드와 동일한 역할을 합니다.
# 다른 파일에서 이 파일을 'import'할 경우, 이 블록 안의 코드는 실행되지 않습니다.
if __name__ == "__main__":
    # --- 1. 페이지 기본 설정 ---
    # st.set_page_config: 브라우저 탭의 제목이나 레이아웃 등 페이지의 전반적인 속성을 설정합니다.
    # Spring에서 application.properties나 yml 파일에 서버 관련 설정을 하는 것과 비유할 수 있습니다.
    st.set_page_config(page_title="YouTube 받아쓰기 앱", layout="centered")
    st.title("📚 YouTube 영어 받아쓰기 앱") # h1 태그에 해당

    # --- 프롬프트 내용 표시 ---
    with st.expander("채점에 사용되는 프롬프트 보기"):
        try:
            # Java에서 파일을 읽는 것과 같이, with open(...) 구문을 사용해 파일을 엽니다.
            # "r"은 읽기 모드, encoding="utf-8"은 한글 등 다양한 문자를 지원하기 위함입니다.
            with open("prompts/evaluation_prompt.md", "r", encoding="utf-8") as f:
                prompt_content = f.read()
            # st.code는 마크다운의 코드 블록(```)처럼 텍스트를 고정폭 글꼴로 보여줍니다.
            st.code(prompt_content, language="markdown")
        except FileNotFoundError:
            # Java의 FileSystemNotFoundException과 유사한 예외 처리입니다.
            st.error("프롬프트 파일을 찾을 수 없습니다: prompts/evaluation_prompt.md")


    st.write(
        "유튜브 영상의 스크립트를 가져와 문장 단위로 받아쓰기 연습을 할 수 있습니다."
    )

    # st.text_input: 사용자로부터 텍스트를 입력받는 UI 컴포넌트를 생성합니다.
    # HTML의 <input type="text">와 같습니다.
    youtube_url = st.text_input(
        "유튜브 영상 URL을 입력하세요:",
        help="예: https://www.youtube.com/watch?v=M-y14-3Y6gE",
    )

    # --- 2. 세션 상태(Session State) 관리 ---
    # st.session_state는 Streamlit이 제공하는 특별한 딕셔너리(Dictionary) 객체입니다.
    # Java/Spring 관점:
    # - 이는 웹 애플리케이션의 '세션(Session)'과 매우 유사합니다. (e.g., 'HttpSession' 객체)
    # - 사용자가 앱과 상호작용(버튼 클릭 등)하여 스크립트가 다시 실행되더라도, st.session_state에 저장된 값은 유지됩니다.
    # - 이를 통해 페이지 간의 상태나 사용자의 진행 상황을 기억할 수 있습니다.
    if "sentences" not in st.session_state:
        # 세션 초기화: 사용자가 처음 접속했거나 세션이 만료되었을 때 필요한 변수들을 초기화합니다.
        # Spring에서 사용자가 처음 로그인했을 때 세션에 사용자 정보를 저장하는 것과 유사합니다.
        st.session_state.sentences = []
        st.session_state.total_sentences = 0
        st.session_state.current_sentence_index = 0
        st.session_state.user_inputs = []
        st.session_state.scores = []

    # st.button: 클릭 가능한 버튼을 생성합니다. 이 함수는 버튼이 클릭되면 True를 반환합니다.
    # 'if st.button(...) :' 구문은 "만약 사용자가 이 버튼을 클릭했다면" 이라는 의미의 이벤트 리스너와 같습니다.
    if st.button("스크립트 가져오기", key="get_script_button"):
        if youtube_url:
            # utils.py에 정의된 함수들을 호출하여 비즈니스 로직을 수행합니다.
            # Spring의 Controller가 Service 계층의 메소드를 호출하는 것과 유사한 흐름입니다.
            video_id = extract_video_id_from_url(youtube_url)
            if video_id:
                # st.spinner: 작업이 진행 중임을 알려주는 로딩 UI를 표시합니다.
                with st.spinner("스크립트를 처리 중입니다..."):
                    original_script = get_youtube_transcript(video_id)

                if original_script:
                    refined_script = clean_script(original_script)
                    sentences = split_into_sentences(refined_script)

                    # 처리된 결과를 세션 상태에 저장하여 다음 상호작용에서도 사용할 수 있도록 합니다.
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

    # --- 3. 받아쓰기 인터페이스 렌더링 ---
    # 세션에 문장 데이터가 있을 경우에만 이 블록의 UI를 그립니다.
    if st.session_state.sentences:
        st.markdown("---") # 구분선(<hr>)

        # 현재 문장 인덱스를 세션에서 가져옵니다.
        idx = st.session_state.current_sentence_index
        total = st.session_state.total_sentences
        st.write(f"**문장 {idx + 1} / {total}**")

        st.subheader("✅ 원본 스크립트")
        st.write(st.session_state.sentences[idx])

        st.subheader("✍️ 당신의 받아쓰기")
        # st.text_area: 여러 줄의 텍스트를 입력받는 UI 컴포넌트. HTML의 <textarea>와 같습니다.
        user_input = st.text_area(
            "영상을 듣고 받아쓰기한 내용을 여기에 입력하세요:",
            value=st.session_state.user_inputs[idx], # 세션에 저장된 값을 기본값으로 표시
            key=f"user_input_{idx}",  # 각 UI 컴포넌트는 고유한 key를 가져야 합니다.
        )
        # 사용자의 입력을 다시 세션에 저장하여, 다른 버튼을 눌러도 내용이 사라지지 않게 합니다.
        st.session_state.user_inputs[idx] = user_input

        # --- 네비게이션 및 채점 버튼 ---
        # st.columns: UI를 여러 열로 나눕니다. CSS의 Flexbox나 Grid와 유사한 레이아웃 기능입니다.
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

        with col1:
            if st.button("이전", disabled=(idx <= 0)):
                st.session_state.current_sentence_index -= 1
                st.rerun() # 스크립트를 즉시 다시 실행하여 UI를 새로고침합니다.

        with col2:
            if st.button("채점하기", use_container_width=True):
                if user_input:
                    with st.spinner("Gemini AI가 채점 중입니다..."):
                        # 'evaluate' 서비스 함수를 호출하고 결과를 세션에 저장합니다.
                        scoring_result = evaluate(
                            st.session_state.sentences[idx], user_input
                        )
                        st.session_state.scores[idx] = scoring_result
                else:
                    st.warning("받아쓰기 내용을 입력해주세요!")

        with col3:
            # 이 부분은 나중에 기능을 추가하기 위해 비워져 있습니다.
            pass

        with col4:
            if st.button("다음", disabled=(idx >= total - 1)):
                st.session_state.current_sentence_index += 1
                st.rerun()

        # --- 4. 채점 결과 표시 ---
        # 현재 문장에 대한 채점 결과가 세션에 있을 경우에만 결과를 표시합니다.
        if st.session_state.scores[idx]:
            # st.expander: 접고 펼 수 있는 UI 컨테이너를 만듭니다.
            with st.expander("채점 결과 보기", expanded=True):
                scoring_results = st.session_state.scores[idx]

                # API 응답에 'error' 키가 있는지 확인하여 오류를 처리합니다.
                if "error" in scoring_results:
                    st.error(f"채점 중 오류 발생: {scoring_results.get('error')}")
                    st.text(f"오류 상세 내용: {scoring_results.get('details')}")
                    st.subheader("Gemini AI 원본 응답:")
                    st.code(scoring_results.get('raw_response'))
                else:
                    # 성공적인 결과 표시
                    st.write(f"**💯 총점:** {scoring_results.get('score')}/100")
                    st.write(
                        f"**👍 잘한 점:** {scoring_results.get('positive_feedback')}"
                    )

                    points = scoring_results.get("points_for_improvement", [])
                    if points:
                        st.write("**✏️ 개선할 점:**")
                        # 리스트를 순회하며 개선점을 하나씩 출력합니다.
                        for point in points:
                            st.markdown(f"- **원본:** `{point.get('original')}`")
                            st.markdown(f"  **입력:** `{point.get('user_input')}`")
                            st.markdown(f"  **제안:** {point.get('suggestion')}\n")
                    else:
                        st.info("훌륭합니다! 특별히 개선할 점이 보이지 않습니다.")

    st.markdown("---")
    st.info("이 앱은 Gemini AI와 YouTube Transcript API를 사용하여 만들어졌습니다.")