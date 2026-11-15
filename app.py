import streamlit as st
import json
import re
from datetime import datetime
import base64
import html
import pandas as pd
from pathlib import Path

# ============================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================
st.set_page_config(page_title="КофеСервис", page_icon="☕", layout="wide", initial_sidebar_state="collapsed")

# ============================================
# ДИЗАЙН
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f2e8dc; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a { display: none !important; }
    [data-testid="stHeaderActionElements"] { display: none !important; }
    
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }
    
    /* ===== ШАПКА ===== */
    .coffee-header {
        position: relative; isolation: isolate; overflow: hidden;
        padding: 30px 28px; margin: 4px 0 26px; border-radius: 24px;
        background: radial-gradient(ellipse at 96% 10%, rgba(121, 85, 72, 0.11) 0%, rgba(121, 85, 72, 0) 62%);
        border-bottom: 1px solid rgba(78, 52, 46, 0.16);
        display: flex; align-items: center; gap: 26px;
    }
    .coffee-header::before, .coffee-header::after {
        content: ""; position: absolute; z-index: -1; pointer-events: none;
        border: 1px solid rgba(78, 52, 46, 0.1); border-radius: 50%;
    }
    .coffee-header::before { width: 270px; height: 270px; right: -55px; top: -105px; }
    .coffee-header::after { width: 205px; height: 205px; right: -22px; top: -72px; }
    
    .coffee-header__logo { width: 100px; flex-shrink: 0; filter: drop-shadow(0 8px 12px rgba(62, 39, 35, 0.16)); }
    .coffee-header__content { min-width: 0; }
    .coffee-header__eyebrow { margin-bottom: 10px; color: #795548; font-size: 11px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; }
    .coffee-header h1.coffee-header__title { margin: 0 !important; color: #3e2723 !important; font-size: clamp(36px, 5vw, 58px) !important; font-weight: 700 !important; letter-spacing: -1.8px; line-height: 1.12 !important; }
    .coffee-header__brand { display: inline-block; position: relative; padding-bottom: 13px; }
    .coffee-header__brand::after { content: ""; position: absolute; left: 1px; bottom: 0; width: 84px; height: 4px; border-radius: 4px; background: linear-gradient(90deg, #4e342e, #a1887f); }
    .coffee-header__subtitle { display: block; margin-top: 12px; color: #5d4037; font-size: clamp(19px, 2.5vw, 27px); font-weight: 500; }
    .coffee-header__description { margin: 12px 0 0; color: #6d5147; font-size: 14px; }
    
    .mode-badge { display: inline-flex; align-items: center; gap: 8px; margin-top: 12px; padding: 6px 11px; border: 1px solid rgba(78, 52, 46, 0.2); border-radius: 20px; color: #5d4037; font-size: 12px; font-weight: 500; background: rgba(242, 232, 220, 0.7); }
    
    /* Общие стили */
    h2 { font-size: 24px !important; font-weight: 700 !important; }
    h3 { font-size: 20px !important; font-weight: 700 !important; }
    .small-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #70554b; margin-bottom: 4px; }
    .value-text { font-size: 17px; font-weight: 600; color: #3e2723; margin-bottom: 15px; overflow-wrap: anywhere; }
    
    /* Карточки */
    .custom-card { border: 3px solid #4e342e !important; border-radius: 16px !important; background-color: transparent !important; box-shadow: 0 2px 5px rgba(62, 39, 35, 0.04), 0 12px 28px -10px rgba(62, 39, 35, 0.18) !important; padding: 25px !important; margin-bottom: 25px !important; position: relative; overflow: hidden; }
    .custom-card::before { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #4e342e 0%, #6d4c41 55%, #2f6f5e 100%); pointer-events: none; }
    
    @keyframes result-enter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .result-card { animation: result-enter 320ms cubic-bezier(0.2, 0.7, 0.2, 1); }
    
    /* Следующее действие */
    .next-action-card { background: #4e342e; color: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid #2f6f5e; }
    .next-action-card h3 { color: white; margin: 0 0 10px 0; }
    .next-action-card p { margin: 0; opacity: 0.9; font-size: 15px; }
    
    /* Запчасти */
    .part-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 18px; margin-bottom: 10px; border: 1px solid rgba(78, 52, 46, 0.2); border-radius: 12px; background: transparent; transition: border-color 180ms ease, box-shadow 180ms ease, background-color 180ms ease; }
    .part-name { color: #3e2723; font-size: 16px; font-weight: 600; overflow-wrap: anywhere; }
    .part-meta { margin-top: 5px; color: #5d4037; font-size: 13px; }
    
    @media (hover: hover) and (pointer: fine) {
        .part-row:hover { border-color: rgba(78, 52, 46, 0.42); background-color: rgba(78, 52, 46, 0.025); box-shadow: 0 4px 10px rgba(62, 39, 35, 0.06); }
    }
    
    /* Кнопки */
    .stButton > button { background: linear-gradient(135deg, #4e342e 0%, #3e2723 100%); color: white !important; border: none; border-radius: 12px; padding: 12px 32px; font-weight: 600; font-size: 16px; width: auto; margin-bottom: 20px; }
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid #2f6f5e; outline-offset: 3px; }
    
    /* Статусы */
    .status-badge { display: inline-flex; align-items: center; gap: 7px; padding: 6px 14px; border-radius: 24px; font-size: 13px; font-weight: 700; }
    .badge-success { background-color: #d9ead9; color: #1b5e20 !important; }
    .badge-warning { background-color: #fff2cc; color: #7a5c00 !important; }
    .badge-danger { background-color: #f8d7da; color: #721c24 !important; }
    .badge-success::before, .badge-warning::before, .badge-danger::before { content: ""; width: 8px; height: 8px; border-radius: 50%; }
    .badge-success::before { background: #2e7d32; } .badge-warning::before { background: #f9a825; } .badge-danger::before { background: #c62828; }
    
    /* Адаптивность */
    @media (max-width: 640px) {
        .coffee-header { align-items: flex-start; gap: 14px; padding: 22px 14px; border-radius: 18px; }
        .coffee-header::before, .coffee-header::after { display: none; }
        .coffee-header__logo { width: 58px; }
        .coffee-header h1.coffee-header__title { font-size: 34px !important; letter-spacing: -1px; }
        .coffee-header__subtitle { font-size: 19px; }
        .custom-card { padding: 18px !important; }
        .result-grid { grid-template-columns: 1fr !important; }
        .part-row { flex-direction: column; align-items: flex-start; }
    }
    
    @media (prefers-reduced-motion: reduce) {
        .result-card { animation: none; }
        .part-row { transition: none; }
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent

# ============================================
# ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ
# ============================================
def validate_data_structure(data):
    if not isinstance(data, dict):
        raise ValueError("Корень data.json должен быть объектом.")
    for section in ("tickets", "equipment", "spare_parts"):
        records = data.get(section)
        if not isinstance(records, list):
            raise ValueError(f"Раздел {section} должен быть списком.")
        if not all(isinstance(item, dict) for item in records):
            raise ValueError(f"Все записи раздела {section} должны быть объектами.")
    if not isinstance(data.get("rules"), dict):
        raise ValueError("Раздел rules должен быть объектом.")
    
    error_codes = data["rules"].get("error_codes", {})
    if not isinstance(error_codes, dict) or not all(isinstance(codes, dict) for codes in error_codes.values()):
        raise ValueError("rules.error_codes должен содержать словари кодов по моделям.")
    
    for index, part in enumerate(data["spare_parts"]):
        for field in ("msk_stock", "msk_res", "tula_stock", "tula_res"):
            if type(part.get(field)) is not int:
                raise ValueError(f"spare_parts[{index}].{field}: ожидалось целое число.")
        if not isinstance(part.get("models"), list):
            raise ValueError(f"spare_parts[{index}].models: ожидался список.")
        if part.get("id") is None or part.get("name") is None:
            raise ValueError(f"spare_parts[{index}]: нужны id и name.")

try:
    with open(BASE_DIR / "data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    validate_data_structure(data)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    st.error(f"Не удалось загрузить data.json: {exc}")
    st.stop()
except ValueError as exc:
    st.error(f"Ошибка структуры данных: {exc}")
    st.stop()

tickets = data.get("tickets", [])
equipment = data.get("equipment", [])
spare_parts = data.get("spare_parts", [])
rules = data.get("rules", {})

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================
def esc(value, fallback="—"):
    text = str(value) if value is not None else ""
    return html.escape(text if text.strip() else fallback)

def normalize_text(value):
    return str(value or "").casefold().replace("ё", "е")

ERROR_CODE_PATTERN = re.compile(r"(?<!\w)[A-Z]\d{2}(?!\w)", flags=re.IGNORECASE)
def extract_error_codes(text):
    return list(dict.fromkeys(match.upper() for match in ERROR_CODE_PATTERN.findall(str(text or ""))))

def serial_matches(serial, text):
    serial = normalize_text(serial).strip()
    text = normalize_text(text)
    if not serial: return False
    pattern = rf"(?<!\w){re.escape(serial)}(?!\w)"
    return re.search(pattern, text) is not None

def find_equipment(text, author):
    text_lower = normalize_text(text)
    author_lower = normalize_text(author)
    candidates = []
    for eq in equipment:
        reasons = []
        score = 0
        serial_match = serial_matches(eq.get("serial", ""), text_lower)
        if serial_match:
            score += 100
            reasons.append(f"Совпал серийный номер: {eq.get('serial')}")
        model = normalize_text(eq.get("model", ""))
        if model and model in text_lower:
            score += 30
            reasons.append(f"Совпала модель: {eq.get('model')}")
        client = normalize_text(eq.get("client", ""))
        if client and (client in text_lower or client in author_lower):
            score += 20
            reasons.append(f"Совпал клиент: {eq.get('client')}")
        if score > 0:
            candidates.append({"eq": eq, "score": score, "reasons": reasons, "serial_match": serial_match})
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates

def get_spare_parts(model, warehouse):
    prefixes = {"Москва": "msk", "Тула": "tula"}
    if warehouse not in prefixes:
        raise ValueError(f"Неизвестный склад: {warehouse}")
    prefix = prefixes[warehouse]
    result = []
    for part in spare_parts:
        if model not in part.get("models", []):
            continue
        stock = part[f"{prefix}_stock"]
        reserved = part[f"{prefix}_res"]
        stock_error = (stock < 0 or reserved < 0 or reserved > stock)
        result.append({
            "id": str(part["id"]),
            "name": str(part["name"]),
            "free": 0 if stock_error else stock - reserved,
            "stock_error": stock_error,
        })
    return result

def generate_questions(text, confidence, threshold=70):
    qs = []
    text_lower = normalize_text(text)
    if confidence < threshold:
        qs.append("Уточните серийный номер машины (на шильдике).")
    if any(word in text_lower for word in ("течет", "течь", "капает", "протекает")):
        qs.append("Где именно появляется вода? (снизу, слева, справа, из-под группы)")
        qs.append("Когда появляется вода? (во время приготовления, после, постоянно)")
    if ("код" in text_lower or "ошибк" in text_lower) and not extract_error_codes(text):
        qs.append("Уточните точный код ошибки с экрана.")
    return list(dict.fromkeys(qs))

def build_client_reply(questions):
    if not questions: return "Здравствуйте! Уточните, пожалуйста, когда появилась неисправность."
    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
    return f"Здравствуйте! Чтобы подготовить выезд инженера, ответьте, пожалуйста:\n\n{numbered}"

def check_warranty(eq):
    today = datetime.now().date()
    for date_field in ("last_visit", "install_date"):
        value = eq.get(date_field)
        if not value: continue
        try:
            event_date = datetime.strptime(value, "%d.%m.%Y").date()
            if 0 <= (today - event_date).days <= 30: return True
        except (ValueError, TypeError):
            pass
    return False

def classify_problem(text):
    text = normalize_text(text)
    categories = [
        ("Не включается", ("не включ", "не запуска")),
        ("Течь", ("течет", "течь", "капает", "протекает")),
        ("Ошибка на экране", ("ошиб", "код")),
        ("Шум / гул", ("шум", "гул", "гудит")),
    ]
    for category, keywords in categories:
        if any(word in text for word in keywords):
            return category
    if ERROR_CODE_PATTERN.search(text):
        return "Ошибка на экране"
    return "Другое / не определено"

def build_analytics(tickets):
    rows = []
    for ticket in tickets:
        text = str(ticket.get("text") or "")
        author = str(ticket.get("author") or "")
        candidates = find_equipment(text, author)
        exact = [c for c in candidates if c.get("serial_match")]
        if len(exact) == 1:
            status, model = "Одно совпадение по S/N", exact[0]["eq"].get("model") or "Не указана"
        elif candidates:
            status, model = "Требует подтверждения", None
        else:
            status, model = "Нет совпадений", None
        rows.append({"Статус": status, "Модель": model, "Тип проблемы": classify_problem(text)})
    return pd.DataFrame(rows)

def image_to_base64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# Загрузка картинок
img_inbox = image_to_base64(BASE_DIR / "inbox.png")
img_result = image_to_base64(BASE_DIR / "result.png")
img_parts = image_to_base64(BASE_DIR / "parts.png")
img_logo = image_to_base64(BASE_DIR / "logo.png")

# Загрузка иконок для разделов (внутри)
img_tab_requests = image_to_base64(BASE_DIR / "tab_requests.png")
img_tab_analytics = image_to_base64(BASE_DIR / "tab_analytics.png")
img_tab_knowledge = image_to_base64(BASE_DIR / "tab_knowledge.png")

# ============================================
# ШАПКА
# ============================================
header_html = (
    '<div class="coffee-header">'
    f'<img class="coffee-header__logo" src="data:image/png;base64,{img_logo}" alt="Логотип">'
    '<div class="coffee-header__content">'
    '<div class="coffee-header__eyebrow">Сервис кофейного оборудования</div>'
    '<h1 class="coffee-header__title"><span class="coffee-header__brand">КофеСервис</span>'
    '<span class="coffee-header__subtitle">Ассистент диспетчера</span></h1>'
    '<p class="coffee-header__description">От обращения — к подготовленному выезду.</p>'
    '<div class="mode-badge">Демо · Разбор по правилам</div>'
    '</div></div>'
)
st.markdown(header_html, unsafe_allow_html=True)

# ============================================
# ВКЛАДКИ (ТЕКСТОВЫЕ)
# ============================================
tab1, tab2, tab3 = st.tabs(["Разбор обращений", "Аналитика", "База знаний"])

# --- ВКЛАДКА 1: РАЗБОР ---
with tab1:
    col_icon, col_title = st.columns([1, 15])
    with col_icon:
        if img_tab_requests:
            st.image(f"data:image/png;base64,{img_tab_requests}", width=40)
    with col_title:
        st.markdown("<h3 style='margin-top: 5px;'>Разбор обращений</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="small-label">Параметры разбора</div>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if tickets:
                ticket_options = [f"{t['id']}: {t['text'][:40]}..." for t in tickets]
                selected_ticket_idx = st.selectbox("Обращение из базы", range(len(tickets)), format_func=lambda i: ticket_options[i])
            else:
                selected_ticket_idx = None
        with col2:
            custom_text = st.text_input("Или введите своё обращение", placeholder="Например: Машина 205 течёт...")
        with col3:
            warehouse = st.selectbox("Склад", ["Москва", "Тула"])

    with st.expander("Настройки разбора"):
        confidence_threshold = st.slider("Порог уверенности (%)", 0, 100, 70)

    if custom_text and custom_text.strip():
        current_text, current_author = custom_text, "Новый клиент"
    elif selected_ticket_idx is not None:
        current_text = tickets[selected_ticket_idx]['text']
        current_author = tickets[selected_ticket_idx]['author']
    else:
        current_text, current_author = "", ""

    if "analysis" not in st.session_state: st.session_state.analysis = None

    # Карточка обращения
    st.markdown(f"""
    <div class="custom-card">
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
            <img src="data:image/png;base64,{img_inbox}" width="64" style="border-radius:14px;">
            <div><div class="small-label">Входящий запрос</div><h3 style="margin:0;">Входящее обращение</h3></div>
        </div>
        <div class="small-label">Автор</div>
        <div class="value-text">{esc(current_author)}</div>
        <div class="small-label">Текст обращения</div>
        <p style='font-size: 18px; line-height: 1.6; color: #333; margin: 5px 0 0 0;'>"{esc(current_text)}"</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Разобрать обращение"):
        if not str(current_text or "").strip():
            st.warning("Введите текст обращения.")
        else:
            with st.spinner("Анализирую обращение..."):
                st.session_state.analysis = {
                    "candidates": find_equipment(current_text, current_author),
                    "text": current_text,
                    "author": current_author,
                    "warehouse": warehouse,
                    "threshold": confidence_threshold,
                    "id": st.session_state.get("analysis_id", 0) + 1,
                }
                st.session_state["analysis_id"] = st.session_state.analysis["id"]

    # Результат
    if st.session_state.analysis:
        res = st.session_state.analysis
        candidates = res["candidates"]
        analysis_id = res["id"]
        
        inputs_changed = (
            current_text != res["text"] or
            current_author != res["author"] or
            warehouse != res["warehouse"] or
            confidence_threshold != res["threshold"]
        )
        if inputs_changed:
            st.warning("Параметры изменились. Ниже показан предыдущий разбор.")
        
        if not candidates:
            st.markdown("""
            <div class="custom-card" style="border-left: 5px solid #e74c3c;">
                <h3 style='color: #e74c3c; margin-top:0;'>Не удалось определить оборудование</h3>
                <p>По правилу П-2: обращение передаётся менеджеру по продажам.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### Нужно уточнить у клиента")
            st.write("- Серийный номер машины (на шильдике).")
            st.write("- Модель кофемашины.")
            st.write("- Описание проблемы.")
        else:
            if len(candidates) > 1:
                selected_idx = st.selectbox(
                    "Выберите кофемашину для подготовки выезда",
                    options=range(len(candidates)),
                    format_func=lambda i: f"S/N {candidates[i]['eq'].get('serial', '—')} · {candidates[i]['eq'].get('model', '—')} · {candidates[i]['eq'].get('address', '—')}",
                    key=f"machine_{analysis_id}"
                )
            else:
                selected_idx = 0
                
            best = candidates[selected_idx]
            eq = best['eq']
            confidence = max(0, min(best['score'], 100))
            reasons = best.get("reasons", [])
            serial_match = best.get("serial_match", False)
            context_id = f"{analysis_id}_{selected_idx}"
            
            if confidence >= 60: badge_class, label = "badge-success", "Высокая уверенность"
            elif confidence >= 30: badge_class, label = "badge-warning", "Требует проверки"
            else: badge_class, label = "badge-danger", "Низкая уверенность"
                
            warranty = check_warranty(eq)
            
            exact_candidates = [c for c in candidates if c.get("serial_match")]
            unique_serial_match = serial_match and len(exact_candidates) == 1
            
            if inputs_changed:
                action_text, action_sub = "Повторить разбор", "Параметры изменились после последнего расчёта."
            elif not unique_serial_match:
                action_text, action_sub = "Подтвердить кофемашину", "Проверьте серийный номер и адрес."
            elif warranty:
                action_text, action_sub = "Проверить основание для гарантии", "Есть дата визита или установки в пределах 30 дней."
            else:
                action_text, action_sub = "Проверить готовность к выезду", "Найдено одно совпадение по S/N. Подтвердите оборудование."

            st.markdown(f"""
            <div class="next-action-card">
                <div class="small-label" style="color: #bcaaa4;">Следующее действие</div>
                <h3>{action_text}</h3>
                <p>{action_sub}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="custom-card result-card">
                <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
                    <img src="data:image/png;base64,{img_result}" width="64" style="border-radius:14px;">
                    <div><div class="small-label">Анализ обращения</div><h3 style="margin:0;">Результат разбора</h3></div>
                </div>
                <div class="result-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <div class="small-label">Клиент</div><div class="value-text">{esc(eq.get('client'))}</div>
                        <div class="small-label">Модель</div><div class="value-text">{esc(eq.get('model'))}</div>
                        <div class="small-label">Серийный номер</div><div class="value-text">{esc(eq.get('serial'))}</div>
                    </div>
                    <div>
                        <div class="small-label">Адрес</div><div class="value-text">{esc(eq.get('address'))}</div>
                        <div class="small-label">Уверенность</div>
                        <div style="margin-bottom: 15px;">
                            <span class='status-badge {badge_class}'>{confidence}% · {label}</span>
                            <div style="height:6px; width:100%; background:rgba(78, 52, 46, 0.12); border-radius:6px; margin-top: 8px;">
                                <div style="height:100%; width:{confidence}%; background:#4e342e; border-radius:6px;"></div>
                            </div>
                        </div>
                        <div class="small-label">Последний визит</div><div class="value-text">{esc(eq.get('last_visit'), 'нет')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Почему предложена эта машина"):
                for reason in reasons: st.write(f"— {reason}")
                st.caption("Процент — оценка совпадения по правилам, а не статистическая вероятность.")

            found_codes = extract_error_codes(res["text"])
            model_error_catalog = rules.get("error_codes", {}).get(eq.get("model"), {})
            if found_codes:
                st.markdown("### Расшифровка кодов")
                for code in found_codes:
                    description = model_error_catalog.get(code)
                    if description:
                        st.info(f"**{code}**: {description}")
                    else:
                        st.warning(f"**{code}**: в справочнике для модели {eq.get('model', '—')} расшифровки нет. Требуется проверка документации.")

            questions = generate_questions(res["text"], confidence, res["threshold"])
            if questions:
                st.markdown("### Нужно уточнить у клиента")
                for q in questions: st.write(f"- {q}")
                with st.expander("Черновик ответа клиенту", expanded=True):
                    st.text_area("Можно отредактировать", value=build_client_reply(questions), height=160, key=f"reply_{context_id}")

            parts = get_spare_parts(eq['model'], res["warehouse"])
            selected_parts = []
            kit_invalid = False
            
            stock_errors = [part["name"] for part in parts if part["stock_error"]]
            if stock_errors:
                st.warning("Обнаружены некорректные складские данные: " + ", ".join(stock_errors) + ". Эти позиции недоступны для подбора до проверки остатков.")
            
            if parts:
                part_rows = []
                for p in parts:
                    if p["stock_error"]:
                        badge_cls, avail = "badge-warning", "Проверить остаток"
                    elif p["free"] > 0:
                        badge_cls, avail = "badge-success", f"Свободно: {p['free']} шт."
                    else:
                        badge_cls, avail = "badge-danger", "Нет свободных"
                    part_rows.append(
                        f'<div class="part-row"><div><div class="part-name">{esc(p["name"])}</div>'
                        f'<div class="part-meta">Артикул: {esc(p["id"])}</div></div>'
                        f'<span class="status-badge {badge_cls}">{avail}</span></div>'
                    )
                
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
                        <img src="data:image/png;base64,{img_parts}" width="64" style="border-radius:14px;">
                        <div><div class="small-label">Склад и резерв</div><h3 style="margin:0;">Доступные запчасти</h3></div>
                    </div>
                    {''.join(part_rows)}
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Собрать комплект инженера"):
                    kit_df = pd.DataFrame([{"Артикул": p["id"], "Название": p["name"], "Свободно": p["free"], "Взять": 0} for p in parts])
                    edited = st.data_editor(kit_df, hide_index=True, disabled=["Артикул", "Название", "Свободно"], column_config={"Взять": st.column_config.NumberColumn(min_value=0, step=1)}, key=f"kit_{context_id}")
                    
                    qty = pd.to_numeric(edited["Взять"], errors="coerce")
                    invalid = qty.isna() | (qty < 0) | (qty > edited["Свободно"]) | (qty % 1 != 0)
                    
                    if invalid.any():
                        st.error("Проверьте комплект: количество должно быть целым и не превышать остаток.")
                        kit_invalid = True
                    else:
                        for index, row in edited.iterrows():
                            quantity = int(qty.loc[index])
                            if quantity > 0:
                                selected_parts.append({"id": str(row["Артикул"]), "name": str(row["Название"]), "qty": quantity})
            else:
                st.info("В справочнике нет совместимых запчастей для выбранной модели. Комплект требует уточнения.")

            st.markdown("### Проверка подготовки")
            machine_confirmed = st.checkbox("Подтверждаю выбранную кофемашину", key=f"confirm_{context_id}")
            warranty_approved = False
            if warranty:
                warranty_approved = st.checkbox("Согласование со старшим инженером получено", key=f"warranty_{context_id}")
                
            issues = []
            if not machine_confirmed: issues.append("Не подтверждена кофемашина.")
            if warranty and not warranty_approved: issues.append("Требуется согласование гарантии.")
            if kit_invalid: issues.append("Некорректное количество запчастей.")
            if inputs_changed: issues.append("Параметры изменились после разбора.")
            if not str(eq.get("address") or "").strip(): issues.append("Не указан адрес выезда.")
            
            if issues:
                st.warning("Предварительная подготовка:\n" + "\n".join(f"- {i}" for i in issues))
            else:
                st.success("Базовые проверки пройдены.")

            st.markdown("<br>", unsafe_allow_html=True)
            report_key = f"report_{context_id}"
            signature_key = f"signature_{context_id}"
            preview_key = f"preview_{context_id}"
            
            report_payload = {
                "equipment": eq,
                "text": res["text"],
                "author": res["author"],
                "warehouse": res["warehouse"],
                "threshold": res["threshold"],
                "parts": selected_parts,
                "machine_confirmed": machine_confirmed,
                "warranty_review": warranty,
                "warranty_approved": warranty_approved,
                "issues": issues,
            }
            current_signature = json.dumps(report_payload, ensure_ascii=False, sort_keys=True)
            
            if st.button("Сформировать карточку инженера", disabled=kit_invalid or inputs_changed):
                status = "ПРЕДВАРИТЕЛЬНАЯ ПОДГОТОВКА" if issues else "БАЗОВЫЕ ПРОВЕРКИ ПРОЙДЕНЫ"
                lines = [
                    "КАРТОЧКА ПОДГОТОВКИ ИНЖЕНЕРА", datetime.now().strftime("%d.%m.%Y %H:%M"),
                    f"Статус: {status}", "", f"Клиент: {eq.get('client', '—')}",
                    f"Адрес: {eq.get('address', '—')}", f"Модель: {eq.get('model', '—')}",
                    f"S/N: {eq.get('serial', '—')}", f"Симптом: {res['text']}",
                    f"Склад: {res['warehouse']}", "", "Комплект:",
                ]
                if selected_parts:
                    lines.extend(f"- {p['name']} ({p['id']}) x{p['qty']}" for p in selected_parts)
                else:
                    lines.append("Комплект не выбран.")
                lines.extend(["", "Открытые вопросы:", *([f"- {issue}" for issue in issues] if issues else ["Нет в рамках выполненных проверок."]), "", "Комплект является планом, не резервом склада."])
                
                report_text = "\n".join(lines)
                st.session_state[report_key] = report_text
                st.session_state[signature_key] = current_signature
                st.session_state[preview_key] = report_text

            if report_key in st.session_state:
                report_stale = (inputs_changed or kit_invalid or st.session_state.get(signature_key) != current_signature)
                if report_stale:
                    st.warning("Карточка устарела: изменились данные. Сформируйте её повторно.")
                
                if preview_key not in st.session_state:
                    st.session_state[preview_key] = st.session_state[report_key]
                    
                st.text_area("Сформированная карточка", height=300, disabled=True, key=preview_key)
                st.download_button("Скачать .txt", data=st.session_state[report_key], file_name=f"card_{eq.get('serial', 'unknown')}.txt", disabled=report_stale, key=f"download_{context_id}")

# --- ВКЛАДКА 2: АНАЛИТИКА ---
with tab2:
    col_icon, col_title = st.columns([1, 15])
    with col_icon:
        if img_tab_analytics:
            st.image(f"data:image/png;base64,{img_tab_analytics}", width=40)
    with col_title:
        st.markdown("<h3 style='margin-top: 5px;'>Аналитика</h3>", unsafe_allow_html=True)
    
    analytics_df = build_analytics(tickets)
    if analytics_df.empty:
        st.info("Нет обращений для анализа.")
    else:
        total = len(analytics_df)
        matched = int((analytics_df["Статус"] == "Одно совпадение по S/N").sum())
        review = int((analytics_df["Статус"] == "Требует подтверждения").sum())
        missing = int((analytics_df["Статус"] == "Нет совпадений").sum())
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Всего обращений", total)
        c2.metric("Совпадение по S/N", matched)
        c3.metric("Нужно подтверждение", review)
        c4.metric("Нет совпадений", missing)
        
        st.markdown("#### Модели в обращениях с совпадением по S/N")
        model_counts = analytics_df["Модель"].dropna().value_counts().head(5).rename("Обращений")
        if not model_counts.empty: st.bar_chart(model_counts, color="#6d4c41")
            
        st.markdown("#### Основной тип проблемы")
        problem_counts = analytics_df["Тип проблемы"].value_counts().rename("Обращений")
        st.bar_chart(problem_counts, color="#2f6f5e")

# --- ВКЛАДКА 3: БАЗА ЗНАНИЙ ---
with tab3:
    col_icon, col_title = st.columns([1, 15])
    with col_icon:
        if img_tab_knowledge:
            st.image(f"data:image/png;base64,{img_tab_knowledge}", width=40)
    with col_title:
        st.markdown("<h3 style='margin-top: 5px;'>База знаний</h3>", unsafe_allow_html=True)
    
    error_catalog = rules.get("error_codes", {})
    if error_catalog:
        kb_model = st.selectbox("Модель для расшифровки кодов", sorted(error_catalog), key="kb_model")
        model_codes = error_catalog.get(kb_model, {})
        for code, description in model_codes.items():
            with st.expander(f"{kb_model} · {code}"):
                st.write(description)
                st.caption("Источник: справочник проекта.")
    else:
        st.info("Справочник кодов пока не заполнен.")
        
    st.markdown("---")
    st.markdown("#### Частые симптомы")
    with st.expander("Течь воды"):
        st.write("Уточнить: где именно появляется вода (снизу, слева, справа, из-под группы).")
        st.write("Уточнить: когда появляется вода (во время приготовления, после, постоянно).")
    with st.expander("Шум / гул"):
        st.write("Уточнить: гул появляется при приготовлении или постоянно.")
    with st.expander("Не включается"):
        st.write("Уточнить: питание включено, вилка в розетке, автомат не выбило.")