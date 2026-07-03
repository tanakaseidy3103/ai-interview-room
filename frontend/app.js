// ⚙️ 設定と定数
const API_URL = 'http://localhost:8000';

const QUESTIONS = [
    "自己紹介をお願いします。これまでの経歴と、今回このポジションに応募された動機についてお聞かせください。",
    "最近直面した最も困難だった技術的課題は何ですか？それをどのように分析し、どのような解決策を選択し、最終的にどのような結果を得たかを説明してください。",
    "重要なプロジェクトの締め切り直前に、予期せぬトラブルで期限に間に合わない可能性が出てきた場合、あなたならチームや関係者とどのようにコミュニケーションを取り、対処しますか？"
];

// 🧠 アプリケーションのグローバル状態管理
let state = {
    candidateName: '',
    sessionId: '',
    currentQuestionIndex: 0,
    stream: null,
    mediaRecorder: null,
    recordedChunks: [],
    isRecording: false,
    timerInterval: null,
    secondsElapsed: 0,
    audioContext: null,
    audioAnalyser: null,
    audioDataArray: null,
    audioAnimationId: null
};

// 🔌 DOM要素の取得
const elements = {
    apiStatusText: document.getElementById('api-status-text'),
    screenWelcome: document.getElementById('screen-welcome'),
    screenInterview: document.getElementById('screen-interview'),
    screenResults: document.getElementById('screen-results'),
    formStartInterview: document.getElementById('form-start-interview'),
    candidateNameInput: document.getElementById('candidate-name'),
    webcamPreview: document.getElementById('webcam-preview'),
    recordingBadge: document.getElementById('recording-badge'),
    recordingStatus: document.getElementById('recording-status'),
    timerBadge: document.getElementById('timer-badge'),
    audioLevelBar: document.getElementById('audio-level-bar'),
    btnRecordAction: document.getElementById('btn-record-action'),
    btnNextQuestion: document.getElementById('btn-next-question'),
    questionText: document.getElementById('question-text'),
    currentQuestionIndexSpan: document.getElementById('current-question-index'),
    totalQuestionsSpan: document.getElementById('total-questions'),
    questionProgressFill: document.getElementById('question-progress-fill'),
    resCandidateName: document.getElementById('res-candidate-name'),
    resSessionId: document.getElementById('res-session-id'),
    resOverallScore: document.getElementById('res-overall-score'),
    resScoreVerdict: document.getElementById('res-score-verdict'),
    resEyeContact: document.getElementById('res-eye-contact'),
    resPosture: document.getElementById('res-posture'),
    resCalm: document.getElementById('res-calm'),
    resExpression: document.getElementById('res-expression'),
    barEyeContact: document.getElementById('bar-eye-contact'),
    barPosture: document.getElementById('bar-posture'),
    barCalm: document.getElementById('bar-calm'),
    barExpression: document.getElementById('bar-expression'),
    resComments: document.getElementById('res-comments'),
    resRecommendations: document.getElementById('res-recommendations'),
    btnRestart: document.getElementById('btn-restart')
};

// 🏁 初期ロード処理
document.addEventListener('DOMContentLoaded', () => {
    checkBackendHealth();
    setupEventListeners();
    elements.totalQuestionsSpan.textContent = QUESTIONS.length;
});

// 🏥 バックエンドサーバーのヘルスチェック
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        if (data.status === 'ok') {
            elements.apiStatusText.innerHTML = `サーバーオンライン`;
            elements.apiStatusText.previousElementSibling.className = 'pulse-dot green';
        } else {
            setServerOfflineState();
        }
    } catch (error) {
        console.error('APIへの接続エラー:', error);
        setServerOfflineState();
    }
}

function setServerOfflineState() {
    elements.apiStatusText.innerHTML = `サーバーオフライン（Dockerを起動してください）`;
    elements.apiStatusText.previousElementSibling.className = 'pulse-dot red';
}

// 🎛️ イベントリスナーのセットアップ
function setupEventListeners() {
    // 案内画面フォームの送信
    elements.formStartInterview.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = elements.candidateNameInput.value.trim();
        if (name) {
            state.candidateName = name;
            await startInterviewSession();
        }
    });

    // 録画開始 / 停止ボタン
    elements.btnRecordAction.addEventListener('click', () => {
        if (!state.isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    // 次の質問へ進む / 完了ボタン
    elements.btnNextQuestion.addEventListener('click', async () => {
        if (state.currentQuestionIndex < QUESTIONS.length - 1) {
            goToNextQuestion();
        } else {
            await finishInterviewAndAnalyze();
        }
    });

    // やり直しボタン
    elements.btnRestart.addEventListener('click', () => {
        resetApp();
    });
}

// 🔀 画面切り替えユーティリティ
function showScreen(screenId) {
    const screens = [elements.screenWelcome, elements.screenInterview, elements.screenResults];
    screens.forEach(screen => {
        if (screen.id === screenId) {
            screen.classList.add('active');
        } else {
            screen.classList.remove('active');
        }
    });
}

// 🎥 面接セッションの開始（セッション登録 & カメラ有効化）
async function startInterviewSession() {
    try {
        // 1. バックエンドでセッションを作成
        const response = await fetch(`${API_URL}/interview/session/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_name: state.candidateName })
        });

        if (!response.ok) throw new Error('セッションの開始に失敗しました。');

        const data = await response.json();
        state.sessionId = data.session_id;

        // 2. カメラとマイクのストリームを取得
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 1280, height: 720, facingMode: "user" },
            audio: true
        });

        state.stream = stream;
        elements.webcamPreview.srcObject = stream;

        // 音声モニターの起動
        setupAudioMonitor(stream);

        // 3. 画面切り替えと最初の質問のロード
        showScreen('screen-interview');
        loadQuestion(0);

    } catch (error) {
        console.error('面接開始エラー:', error);
        alert(`カメラ/マイクへのアクセス、またはバックエンドへの接続に失敗しました。権限を許可し、Dockerが起動していることを確認してください。\n\n詳細: ${error.message}`);
    }
}

// 🎙️ マイク入力レベルの可視化モニター
function setupAudioMonitor(stream) {
    try {
        state.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = state.audioContext.createMediaStreamSource(stream);
        state.audioAnalyser = state.audioContext.createAnalyser();
        state.audioAnalyser.fftSize = 256;
        source.connect(state.audioAnalyser);

        const bufferLength = state.audioAnalyser.frequencyBinCount;
        state.audioDataArray = new Uint8Array(bufferLength);

        function drawVolume() {
            if (!state.stream) return;
            state.audioAnalyser.getByteFrequencyData(state.audioDataArray);
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += state.audioDataArray[i];
            }
            const average = sum / bufferLength;
            // 音量レベルを正規化して幅を更新
            const percentage = Math.min(100, Math.round((average / 120) * 100));
            elements.audioLevelBar.style.width = `${percentage}%`;
            state.audioAnimationId = requestAnimationFrame(drawVolume);
        }
        drawVolume();
    } catch (e) {
        console.warn('マイクモニターの設定エラー:', e);
    }
}

// 📝 質問の読み込み
function loadQuestion(index) {
    state.currentQuestionIndex = index;
    elements.questionText.textContent = QUESTIONS[index];
    elements.currentQuestionIndexSpan.textContent = index + 1;
    
    // 進捗バーの更新
    const progressPercent = ((index + 1) / QUESTIONS.length) * 100;
    elements.questionProgressFill.style.width = `${progressPercent}%`;

    // 進行ボタンのテキスト更新
    if (index === QUESTIONS.length - 1) {
        elements.btnNextQuestion.innerHTML = `面接を完了して結果を見る 🚀`;
    } else {
        elements.btnNextQuestion.innerHTML = `次の質問へ <span class="arrow">→</span>`;
    }

    // 録画完了するまで次の質問へ進めないようロック
    elements.btnNextQuestion.disabled = true;
    
    // 録画ボタン状態の初期化
    elements.btnRecordAction.className = 'btn btn-record btn-large';
    elements.btnRecordAction.innerHTML = `<span class="icon">🔴</span> 録画を開始する`;
    elements.btnRecordAction.disabled = false;
    
    elements.recordingStatus.textContent = '録画開始待ち';
    elements.recordingBadge.querySelector('.pulse-dot').className = 'pulse-dot red';
    elements.timerBadge.textContent = '00:00';
}

// 🔴 録画開始
function startRecording() {
    state.recordedChunks = [];
    
    // ブラウザ毎の対応コーデックの判定
    let options = { mimeType: 'video/webm;codecs=vp9,opus' };
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'video/webm;codecs=vp8,opus' };
    }
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'video/webm' };
    }
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'video/mp4' }; // Safari対応
    }

    try {
        state.mediaRecorder = new MediaRecorder(state.stream, options);
        
        state.mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                state.recordedChunks.push(event.data);
            }
        };

        state.mediaRecorder.onstop = async () => {
            await handleRecordedVideo();
        };

        state.mediaRecorder.start(1000); // 1秒ごとにチャンクを取得
        state.isRecording = true;
        
        // UI状態変更
        elements.btnRecordAction.className = 'btn btn-record recording btn-large';
        elements.btnRecordAction.innerHTML = `<span class="icon">⏹️</span> 録画を停止する`;
        elements.recordingStatus.textContent = '録画中...';
        elements.recordingBadge.querySelector('.pulse-dot').className = 'pulse-dot red';
        
        startTimer();
    } catch (e) {
        console.error('MediaRecorderの起動失敗:', e);
        alert('録画の開始に失敗しました。お使いのブラウザは録画機能をサポートしていない可能性があります。');
    }
}

// ⏹️ 録画停止
function stopRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.mediaRecorder.stop();
        state.isRecording = false;
        stopTimer();
        elements.btnRecordAction.disabled = true;
        elements.btnRecordAction.innerHTML = `⏳ 動画処理中...`;
        elements.recordingStatus.textContent = '動画を処理中...';
    }
}

// ⏱️ タイマー計測
function startTimer() {
    state.secondsElapsed = 0;
    elements.timerBadge.textContent = '00:00';
    state.timerInterval = setInterval(() => {
        state.secondsElapsed++;
        const minutes = Math.floor(state.secondsElapsed / 60).toString().padStart(2, '0');
        const seconds = (state.secondsElapsed % 60).toString().padStart(2, '0');
        elements.timerBadge.textContent = `${minutes}:${seconds}`;
    }, 1000);
}

function stopTimer() {
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
    }
}

// 📤 録画したビデオデータのサーバーアップロード
async function handleRecordedVideo() {
    const videoBlob = new Blob(state.recordedChunks, { type: state.mediaRecorder.mimeType || 'video/webm' });
    
    // アップロード用 FormData の構築
    const formData = new FormData();
    const extension = videoBlob.type.includes('mp4') ? 'mp4' : 'webm';
    formData.append('file', videoBlob, `response_q_${state.currentQuestionIndex + 1}.${extension}`);

    try {
        const response = await fetch(`${API_URL}/interview/video/upload?session_id=${state.sessionId}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('サーバーへの動画アップロードに失敗しました。');

        const data = await response.json();
        console.log('動画送信成功:', data);

        // UI更新
        elements.btnRecordAction.className = 'btn btn-record btn-large';
        elements.btnRecordAction.innerHTML = `✅ 保存・送信完了！`;
        elements.recordingStatus.textContent = '回答が保存されました！';
        elements.btnNextQuestion.disabled = false; // 次のステップを有効化

    } catch (e) {
        console.error('動画アップロードエラー:', e);
        elements.btnRecordAction.className = 'btn btn-record btn-large';
        elements.btnRecordAction.innerHTML = `❌ 送信エラー`;
        elements.recordingStatus.textContent = '動画の保存に失敗しました。';
        elements.btnRecordAction.disabled = false;
        alert('動画のアップロード中にエラーが発生しました。Dockerコンテナの状態を確認してください。');
    }
}

// ➡️ 次の質問へ移行
function goToNextQuestion() {
    loadQuestion(state.currentQuestionIndex + 1);
}

// 🏁 面接完了とAI分析の開始
async function finishInterviewAndAnalyze() {
    elements.btnNextQuestion.disabled = true;
    elements.btnNextQuestion.innerHTML = `⏳ AIによる行動分析中...`;

    try {
        // 1. 分析開始要求 (Mock呼び出し)
        await fetch(`${API_URL}/interview/analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                questions: QUESTIONS
            })
        });

        // 2. 分析結果フィードバックデータを作成してDynamoDBに保存
        const dynamicScores = generateMockScores();
        
        await fetch(`${API_URL}/interview/feedback/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                feedback: dynamicScores
            })
        });

        // 3. 保存された評価結果を読み込み
        const getRes = await fetch(`${API_URL}/interview/feedback/${state.sessionId}`);
        if (!getRes.ok) throw new Error('フィードバックデータの取得に失敗しました。');
        
        const feedbackData = await getRes.json();
        
        // 4. ハードウェアへの負担を下げるためカメラを停止
        stopCamera();

        // 5. 結果画面を描画
        displayResults(feedbackData);

    } catch (e) {
        console.error('面接完了処理エラー:', e);
        alert('分析の実行中にエラーが発生しました。バックエンドコンテナの状態を確認してください。');
        elements.btnNextQuestion.disabled = false;
        elements.btnNextQuestion.innerHTML = `面接を完了して結果を見る 🚀`;
    }
}

// 📐 ポートフォリオ評価用の現実的なモックスコア自動生成
function generateMockScores() {
    const eyeContact = Math.floor(Math.random() * 3) + 7; // 7〜9点
    const posture = Math.floor(Math.random() * 3) + 7;
    const nervousness = Math.floor(Math.random() * 3) + 7;
    const expression = Math.floor(Math.random() * 4) + 6; // 6〜9点
    const overall = Math.round((eyeContact + posture + nervousness + expression) / 4);

    const commentsList = [
        "論理的で明瞭な話し方ができており、技術的な経歴アピールも非常に簡潔で分かりやすかったです。相手を安心させるトーンで好印象でした。",
        "難解な技術課題に関する質問に対しても、結論ファーストかつ一貫した構成で答えることができており、高い問題解決能力が伝わりました。",
        "カメラを面接官と見立てて安定した目線を維持できており、適度な身振り手振りを交えながら熱意を持って自己表現ができていました。"
    ];
    
    const recsList = [
        "複雑なコード設計などについて考える際、視線が上や左右に泳ぎやすいため、常にカメラレンズの奥を意識するとより面接官にアピールできます。",
        "少し緊張が見られ、肩や首に力が入っている瞬間がありました。発言の合間に深く呼吸をしてリラックスした姿勢をとるとさらに良くなります。",
        "高度な概念について話す場合、回答をすぐに始めるのではなく、頭の中で1〜2秒ほど論理的な構成を組み立ててから話し始めると、一層明快になります。"
    ];

    return {
        eye_contact_score: eyeContact,
        posture_score: posture,
        nervousness_score: nervousness,
        expression_score: expression,
        overall_score: overall,
        comments: commentsList[Math.floor(Math.random() * commentsList.length)],
        recommendations: recsList
    };
}

// 🔌 カメラストリームの停止処理
function stopCamera() {
    if (state.stream) {
        state.stream.getTracks().forEach(track => track.stop());
        state.stream = null;
    }
    if (state.audioAnimationId) {
        cancelAnimationFrame(state.audioAnimationId);
    }
    if (state.audioContext) {
        state.audioContext.close();
    }
}

// 📊 結果レポートのレンダリング
function displayResults(data) {
    const fb = data.feedback || data; // レスポンス構造の差分吸収
    
    elements.resCandidateName.textContent = state.candidateName;
    elements.resSessionId.textContent = state.sessionId;
    
    elements.resOverallScore.textContent = fb.overall_score;
    elements.resComments.textContent = fb.comments;

    // スコアに応じた評価メッセージとスタイルの適用
    if (fb.overall_score >= 8) {
        elements.resScoreVerdict.textContent = "大変優秀な評価です！ 🌟";
        elements.resScoreVerdict.style.color = "var(--success-color)";
    } else if (fb.overall_score >= 6) {
        elements.resScoreVerdict.textContent = "良好な評価です（一部改善の余地あり） 👍";
        elements.resScoreVerdict.style.color = "var(--primary-color)";
    } else {
        elements.resScoreVerdict.textContent = "要トレーニング評価です ⚠️";
        elements.resScoreVerdict.style.color = "var(--alert-color)";
    }

    // 評価の数値とゲージの描画
    elements.resEyeContact.textContent = `${fb.eye_contact_score}/10`;
    elements.barEyeContact.style.width = `${fb.eye_contact_score * 10}%`;

    elements.resPosture.textContent = `${fb.posture_score}/10`;
    elements.barPosture.style.width = `${fb.posture_score * 10}%`;

    elements.resCalm.textContent = `${fb.nervousness_score}/10`;
    elements.barCalm.style.width = `${fb.nervousness_score * 10}%`;

    elements.resExpression.textContent = `${fb.expression_score}/10`;
    elements.barExpression.style.width = `${fb.expression_score * 10}%`;

    // 改善アドバイスリストの挿入
    elements.resRecommendations.innerHTML = '';
    const recs = fb.recommendations || [];
    recs.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        elements.resRecommendations.appendChild(li);
    });

    // 画面の切り替え
    showScreen('screen-results');
}

// 🔄 状態リセット・最初の画面に戻る
function resetApp() {
    stopCamera();
    state.candidateName = '';
    state.sessionId = '';
    state.currentQuestionIndex = 0;
    state.recordedChunks = [];
    state.isRecording = false;
    elements.candidateNameInput.value = '';
    
    showScreen('screen-welcome');
}
