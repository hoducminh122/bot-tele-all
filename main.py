import os
import requests
import logging
import re
from urllib.parse import urlsplit, urlunsplit, unquote, quote_plus
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time  # thêm import time

# --- NEW IMPORTS ---
import subprocess
import shlex
import json
import secrets
from datetime import datetime, timedelta
# --- END NEW IMPORTS ---

# ============== CONFIG ==============
BOT_TOKEN = "7810405245:AAEvgzgKIunIT57vb-qa7ETHQ3x91XGCSOc"   # 🔑 Thay bằng token từ BotFather

# --- NEW CONFIG ---
ADMINS = [6644473823,7055636268]
KEYS_FILE = "keys.json"
# --- END NEW CONFIG ---

API_DOWNLOAD_BASE = "https://adidaphat.site/xvideos/download?url="
API_SEARCH_BASE = "https://adidaphat.site/xvideos?q="

API_CLIPHOT_SEARCH = "https://adidaphat.site/clipphot?action=search&q="
API_CLIPHOT_DOWNLOAD = "https://adidaphat.site/clipphot?action=download&url="

# add TikTok download API base
API_TT_DOWNLOAD = "https://adidaphat.site/tiktok?type=download&url="

# Logging: chỉ hiển thị WARNING trở lên
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# lưu thời điểm bot khởi động
BOT_START_TIME = time.time()


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
		"👋\n\n"
		"Danh sách toàn bộ lệnh của bot (nhóm theo dịch vụ):\n\n"
		"— Tổng quan —\n"
		"🔸 /start — Hiện trợ giúp\n"
		"🔸 /help  — Xem hướng dẫn (giống /start)\n"
		"🔸 /time  — Thời gian hoạt động Bot\n\n"
		"— Xvideos —\n"
		"📥 /taixvideos <url>\n"
		"🔍 /timxvideos <từ khóa>\n\n"
		"— ClipHot —\n"
		"📥 /taicliphot <url>\n"
		"🔍 /timcliphot <từ khóa>\n\n"
		"— TikTok —\n"
		"🔍 /infott <username>\n"
		"📥 /taivideott <url>\n"
		"🔎 /trendtt\n"
		"🔎 /tukhoatt <từ khóa>\n"
		"👤 /postusertt <username>\n\n"
		"— GitHub —\n"
		"🔍 /infogithub <username>\n\n"
		"— Facebook —\n"
		"🔍 /infofb <uid>\n"
		"⏱ /timefb <uid>\n"
		"🎬 /videofb <url>\n\n"
		"— YouTube —\n"
		"🎥 /videoyt <url>\n\n"
		"— Hình ảnh & Tiện ích —\n"
		"🖼 /xoanen <url>         → Xóa nền ảnh\n"
		"🧓 /doantuoi <url>       → Đoán tuổi từ ảnh\n"
		"☎️ /sdt <số>            → Định giá số điện thoại\n"
		"🖌 /taoanhai <prompt>    → Tạo ảnh AI từ prompt\n"
		"🏧 /vcb <stk> <tien> <noidung> <ctk>\n"
		"🏧 /mb  <stk> <tien> <noidung> <ctk>\n"
		"🏧 /vtb <stk> <tien> <noidung> <ctk>\n"
		"📲 /momo <stk> <tien> <noidung>\n\n"
		"— Quản lý Key & Quyền —\n"
		"🔐 /taokey <số_lượng> <số_ngày> <số_giờ>   (Admin)\n"
		"🔐 /listkey                                (Admin)\n"
		"🔐 /xoakey <key>                            (Admin)\n"
		"🔐 /key <key>                               (kích hoạt key)\n"
		"🔐 /user                                    (đếm người dùng key)\n"
		"🔐 /admin                                   (danh sách admin)\n"
		"🔐 /clearkeyadmin                           (Admin) xóa id admin khỏi các key\n\n"
		"— SQLMap (cần key hợp lệ) —\n"
		"🛠 /sqli <URL>      — Quét SQLi\n"
		"🛠 /tables <URL> <db_name> — Liệt kê bảng\n"
		"🛠 /dump <URL> <db_name>   — Dump/hiện dữ liệu (nếu có)\n\n"
		"Ví dụ nhanh:\n"
		"• /taixvideos https://...\n"
		"• /taokey 5 7 0   (tạo 5 key, 7 ngày)\n\n"
		"Tip: Các kết quả tốt nhất khi dùng trình duyệt Chrome/Firefox/Edge.\n"
		"Gõ /help để xem lại hướng dẫn này bất cứ lúc nào."
	)


# /help -> reuse start content
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await start(update, context)


# /taixvideos <url>
async def taixvideos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Dùng: /taixvideos <url>")
        return

    url = context.args[0]
    api_url = API_DOWNLOAD_BASE + url

    try:
        r = requests.get(api_url, timeout=20)
        j = r.json()

        if not j.get("success"):
            await update.message.reply_text("❌ API trả về lỗi.")
            return

        data = j["data"]
        title = data.get("title", "No title")
        thumb = data["thumbnail"].get("default")
        video_high = data["videoUrls"].get("high")
        video_low = data["videoUrls"].get("low")

        # Inline buttons
        buttons = [
            [InlineKeyboardButton("▶️ High", url=video_high)],
            [InlineKeyboardButton("▶️ Low", url=video_low)],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        caption = f"<b>{title}</b>\n\nChọn link để xem/tải:"
        await update.message.reply_photo(
            photo=thumb, caption=caption, parse_mode="HTML", reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /timxvideos <keyword>
async def timxvideos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Dùng: /timxvideos <từ khóa>")
        return

    keyword = " ".join(context.args)
    api_url = API_SEARCH_BASE + keyword

    try:
        r = requests.get(api_url, timeout=20)
        j = r.json()

        results = j.get("data") or j.get("results") or []
        if not results:
            await update.message.reply_text("❌ Không tìm thấy kết quả.")
            return

        text_lines = []
        for item in results[:8]:  # chỉ hiện tối đa 8 kết quả
            title = item.get("title", "No title")
            link = item.get("url", "")
            text_lines.append(f"• <b>{title}</b>\n<a href='{link}'>{link}</a>")

        await update.message.reply_text(
            "\n\n".join(text_lines), parse_mode="HTML", disable_web_page_preview=False
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# helpers: remove combining diacritics and clean URLs
def remove_diacritics(s: str) -> str:
    if not s:
        return s
    normalized = unicodedata.normalize("NFD", s)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", stripped)


def clean_for_api(input_url: str) -> str:
    """
    Prepare the user-provided Clipphot URL for the download API:
    - percent-decode each component
    - remove combining diacritics (so no percent-encoded sequences remain)
    - remove any '%' characters
    - preserve slashes/hyphens (do NOT insert extra hyphens)
    - drop query/fragment
    """
    if not input_url:
        return input_url
    try:
        parts = urlsplit(input_url)
        scheme = parts.scheme or "https"
        netloc = parts.netloc
        # If netloc missing but user passed full URL, try to handle it
        if not netloc and parts.path and "://" in input_url:
            # fallback: take raw split
            tmp = input_url
            parts = urlsplit(tmp)
            netloc = parts.netloc
        # decode and remove diacritics on path
        raw_path = unquote(parts.path or "")
        raw_path = remove_diacritics(raw_path)
        raw_path = raw_path.replace("%", "")  # ensure no percent signs
        new_url = urlunsplit((scheme, netloc, raw_path, "", ""))
        return new_url
    except Exception:
        # best-effort fallback
        return input_url.replace("%", "")


def normalize_clipphot_display_link(url: str) -> str:
    """
    Normalize a link for display in /timcliphot:
    - decode percent-encoding
    - remove combining diacritics
    - remove any '%' characters
    - preserve original separators (slashes, hyphens)
    """
    if not url:
        return url
    try:
        parts = urlsplit(url)
        path = unquote(parts.path or "")
        path = remove_diacritics(path)
        path = path.replace("%", "")
        query = unquote(parts.query or "").replace("%", "")
        fragment = unquote(parts.fragment or "").replace("%", "")
        return urlunsplit((parts.scheme, parts.netloc, path, query, fragment))
    except Exception:
        return url.replace("%", "")


# /taicliphot <url>
async def taicliphot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Dùng: /taicliphot <url>")
        return

    url = context.args[0].strip()
    sanitized = clean_for_api(url)
    api_url = API_CLIPHOT_DOWNLOAD + sanitized

    try:
        r = requests.get(api_url, timeout=20)
        j = r.json()

        # extract possible fields robustly
        download_url = j.get("downloadUrl") or j.get("download_url")
        source_url = j.get("sourceUrl") or j.get("source_url") or j.get("source")
        data = j.get("data") or {}

        download_url = download_url or data.get("downloadUrl") or data.get("download_url") or data.get("videoUrl") or data.get("video_url")
        source_url = source_url or data.get("sourceUrl") or data.get("source_url") or data.get("source") or data.get("link") or j.get("source")

        title = data.get("title") or j.get("title") or "No title"
        thumb = data.get("thumbnail") or j.get("thumbnail")

        if not (download_url or source_url):
            await update.message.reply_text("❌ API trả về lỗi hoặc không có link.")
            return

        buttons = []
        if download_url:
            buttons.append([InlineKeyboardButton("▶️ Tải/Xem", url=download_url)])
        if source_url:
            buttons.append([InlineKeyboardButton("🔗 Nguồn", url=source_url)])
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

        caption_lines = [f"<b>{title}</b>", ""]
        if download_url:
            caption_lines.append(f"Download: {download_url}")
        if source_url:
            caption_lines.append(f"Source: {source_url}")
        caption = "\n".join(caption_lines)

        # If thumbnail present, send photo; otherwise send text with links (avoids "no photo" error)
        if thumb:
            photo_caption, extra = split_caption(caption)
            await update.message.reply_photo(
                photo=thumb, caption=photo_caption, parse_mode="HTML", reply_markup=reply_markup
            )
            if extra:
                # send remaining text as a follow-up message
                await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
        else:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=False
            )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /timcliphot <keyword>
async def timcliphot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Dùng: /timcliphot <từ khóa>")
        return

    keyword = " ".join(context.args)
    api_url = API_CLIPHOT_SEARCH + keyword

    try:
        r = requests.get(api_url, timeout=20)
        j = r.json()

        results = j.get("results") or j.get("data") or []
        if not results:
            await update.message.reply_text("❌ Không tìm thấy kết quả.")
            return

        text_lines = []
        for item in results[:8]:  # chỉ hiện tối đa 8 kết quả
            title = item.get("title", "No title")
            link = item.get("link", "") or item.get("url", "")
            display_link = normalize_clipphot_display_link(link)
            text_lines.append(f"• <b>{title}</b>\n<a href='{display_link}'>{display_link}</a>")

        await update.message.reply_text(
            "\n\n".join(text_lines), parse_mode="HTML", disable_web_page_preview=False
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /taivideott <url>
async def taivideott(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /taivideott <url>")
		return

	url = context.args[0].strip()
	sanitized = clean_for_api(url)
	api_url = API_TT_DOWNLOAD + sanitized

	try:
		r = requests.get(api_url, timeout=25)
		j = r.json()

		if j.get("code") is not None and j.get("code") != 0:
			# API returned an error code
			await update.message.reply_text("❌ API trả về lỗi.")
			return

		data = j.get("data") or {}

		vid = data.get("id") or data.get("video_id") or ""
		title = data.get("title") or "No title"
		cover = data.get("cover") or data.get("origin_cover") or data.get("ai_dynamic_cover")
		duration = data.get("duration")
		play = data.get("play")  # likely no-watermark or play url
		wmplay = data.get("wmplay")  # watermark
		hdplay = data.get("hdplay") or data.get("play")  # prefer hdplay if available

		# Build buttons in order of preference
		buttons = []
		if hdplay:
			buttons.append([InlineKeyboardButton("▶️ HD", url=hdplay)])
		if play:
			buttons.append([InlineKeyboardButton("▶️ NoWM", url=play)])
		if wmplay:
			buttons.append([InlineKeyboardButton("▶️ WM", url=wmplay)])

		reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

		# Compose caption
		caption_lines = [f"<b>{title}</b>", f"ID: {vid}" if vid else ""]
		if duration:
			caption_lines.append(f"Duration: {duration}s")
		caption_lines.append("")  # separator
		if hdplay:
			caption_lines.append(f"HD: {hdplay}")
		if play:
			caption_lines.append(f"NoWM: {play}")
		if wmplay:
			caption_lines.append(f"WM: {wmplay}")
		caption = "\n".join([ln for ln in caption_lines if ln])

		# Send cover photo with caption if available, otherwise send text
		if cover:
			photo_caption, extra = split_caption(caption)
			await update.message.reply_photo(photo=cover, caption=photo_caption, parse_mode="HTML", reply_markup=reply_markup)
			if extra:
				await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
		else:
			await update.message.reply_text(caption, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# helper: simple HTML escape for user-provided text used in captions
def html_escape(s: str) -> str:
	if not s:
		return ""
	return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --- NEW: MD5/hex utilities and command ---
def calculate_md5_probabilities(hex_str: str):
	"""Validate 32-char hex and compute last5 sum, percentages and suggestion."""
	if not hex_str or len(hex_str) != 32:
		return None, "❌ Vui lòng cung cấp chuỗi hex 32 ký tự."
	# ensure it's valid hex
	try:
		int(hex_str, 16)
	except ValueError:
		return None, "❌ Chuỗi không phải hex hợp lệ."
	last5 = hex_str[-5:]
	try:
		total = sum(int(c, 16) for c in last5)
	except Exception:
		return None, "❌ Lỗi khi phân tích 5 ký tự cuối."
	tai = total
	xiu = 80 - total
	tai_p = round(tai / 80 * 100, 2)
	xiu_p = round(xiu / 80 * 100, 2)
	recommend = "🎯 Tài" if tai_p > xiu_p else "🎯 Xỉu"
	return {
		"md5": hex_str,
		"last5": last5,
		"total": total,
		"tai_percent": tai_p,
		"xiu_percent": xiu_p,
		"recommend": recommend
	}, None

async def md5_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Usage: /md5 <32-hex-string>"""
	if not context.args:
		await update.message.reply_text("❌ Dùng: /md5 <32-hex-string>")
		return
	hex_input = context.args[0].strip().lower()
	res, err = calculate_md5_probabilities(hex_input)
	if err:
		await update.message.reply_text(err)
		return
	msg = (
		f"<b>🔍 MD5 phân tích</b>\n"
		f"🔑 Mã: <code>{html_escape(res['md5'])}</code>\n"
		f"🧩 5 ký tự cuối: <code>{html_escape(res['last5'])}</code>\n"
		f"➕ Tổng: <code>{res['total']}</code>\n"
		f"📊 Xác suất: 🔴 Tài <b>{res['tai_percent']}%</b>  •  🔵 Xỉu <b>{res['xiu_percent']}%</b>\n"
		f"🎲 Gợi ý: {res['recommend']}\n"
	)
	await update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
# --- END NEW: MD5/hex utilities and command ---

# /infott <username>
async def infott(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /infott <username>")
		return

	unique_id = context.args[0].lstrip("@").strip()
	api_url = f"https://adidaphat.site/tiktok?type=userinfo&unique_id={unique_id}"

	try:
		r = requests.get(api_url, timeout=15)
		j = r.json()
		# API returns fields at top-level per sample
		user_id = j.get("id")
		nickname = j.get("nickname") or ""
		username = j.get("username") or unique_id
		avatar = j.get("avatar")
		signature = j.get("signature") or ""
		stats = j.get("stats") or {}

		videos = stats.get("videos", 0)
		following = stats.get("following", 0)
		followers = stats.get("followers", 0)
		likes = stats.get("likes", 0)

		caption_lines = [
			f"<b>{html_escape(nickname)}</b>",
			f"@{html_escape(username)}" if username else "",
			f"ID: {html_escape(user_id)}" if user_id else "",
			"",
			"<b>Giới Tính:</b>",
			html_escape(signature),
			"",
			"<b>Stats</b>",
			f"Videos: {videos}\n  •  Following: {following}\n  •  Followers: {followers}\n  •  Likes: {likes}",
		]
		caption = "\n".join([ln for ln in caption_lines if ln is not None and ln != ""])

		# send avatar if present, otherwise send text
		if avatar:
			photo_caption, extra = split_caption(caption)
			await update.message.reply_photo(photo=avatar, caption=photo_caption, parse_mode="HTML")
			if extra:
				await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
		else:
			await update.message.reply_text(caption, parse_mode="HTML", disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /infogithub <username>
async def infogithub(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /infogithub <username>")
		return

	username = context.args[0].strip()
	api_url = f"https://adidaphat.site/github/info?username={username}"

	try:
		r = requests.get(api_url, timeout=15)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ Không có dữ liệu từ API hoặc user không tồn tại.")
			return

		login = j.get("login") or ""
		name = j.get("name") or ""
		avatar = j.get("avatar_url") or j.get("avatar") or ""
		gid = j.get("id") or ""
		html_url = j.get("html_url") or ""
		public_repos = j.get("public_repos", 0)
		followers = j.get("followers", 0)
		following = j.get("following", 0)
		ngay_tao = j.get("ngay_tao") or j.get("created_at") or ""
		gio_tao = j.get("gio_tao") or ""
		bio = j.get("bio") or ""
		location = j.get("location") or ""

		lines = [
			f"<b>{html_escape(name) or html_escape(login)}</b>",
			f"Login: {html_escape(login)}" if login else "",
			f"ID: {html_escape(str(gid))}" if gid else "",
			f"<a href='{html_escape(html_url)}'>{html_escape(html_url)}</a>" if html_url else "",
			"",
			f"<b>Bio:</b> {html_escape(bio)}" if bio else "",
			f"<b>Location:</b> {html_escape(location)}" if location else "",
			"",
			"<b>Stats</b>",
			f"Public repos: {public_repos}  •  Followers: {followers}  •  Following: {following}",
			"",
			f"Created: {html_escape(ngay_tao)} {html_escape(gio_tao)}",
		]
		caption = "\n".join([ln for ln in lines if ln])

		# send avatar if present, otherwise send text
		if avatar:
			photo_caption, extra = split_caption(caption)
			await update.message.reply_photo(photo=avatar, caption=photo_caption, parse_mode="HTML")
			if extra:
				await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
		else:
			await update.message.reply_text(caption, parse_mode="HTML", disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /infofb <uid>
async def infofb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /infofb <uid>")
		return

	uid = context.args[0].strip()
	api_url = f"https://adidaphat.site/facebook/getinfo?uid={uid}&apikey=apikeysumi"

	try:
		r = requests.get(api_url, timeout=15)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ Không có dữ liệu từ API hoặc uid không tồn tại.")
			return

		avatar = j.get("avatar") or j.get("avatar_url") or j.get("picture") or j.get("photo")

		# Preferred ordering for display
		order = ("name", "username", "first_name", "uid", "link_profile", "created_time",
				 "birthday", "follower", "tichxanh", "relationship_status", "love",
				 "web", "hometown", "locale", "quotes", "about")
		lines = []
		for key in order:
			if key in j:
				val = j.get(key)
				if isinstance(val, bool):
					val = "Yes" if val else "No"
				elif val is None:
					val = ""
				lines.append(f"<b>{html_escape(key)}:</b> {html_escape(str(val))}" if val != "" else f"<b>{html_escape(key)}:</b> —")

		# append any remaining keys (skip avatar-related keys and 'author' explicitly)
		for k, v in j.items():
			if k in order or k in ("avatar", "avatar_url", "picture", "photo", "author"):
				continue
			val_s = "" if v is None else str(v)
			lines.append(f"<b>{html_escape(str(k))}:</b> {html_escape(val_s)}")

		caption = "\n".join(lines) if lines else "No details."

		# send avatar if present, otherwise send text; split long captions for photos
		if avatar:
			photo_caption, extra = split_caption(caption)
			await update.message.reply_photo(photo=avatar, caption=photo_caption, parse_mode="HTML")
			if extra:
				await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
		else:
			await update.message.reply_text(caption, parse_mode="HTML", disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /timefb <uid> - show account creation time
async def timefb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /timefb <uid>")
		return

	uid = context.args[0].strip()
	api_url = f"https://adidaphat.site/facebook/timejoine?uid={uid}&apikey=apikeysumi"

	try:
		r = requests.get(api_url, timeout=15)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ Không có dữ liệu từ API hoặc uid không tồn tại.")
			return

		# Extract fields, skip 'author' if present
		name = j.get("name") or j.get("fullname") or ""
		day = j.get("day") or j.get("date") or ""
		time_v = j.get("time") or j.get("hour") or ""
		uid_ret = j.get("uid") or uid

		lines = []
		if name:
			lines.append(f"<b>Name:</b> {html_escape(str(name))}")
		if uid_ret:
			lines.append(f"<b>UID:</b> {html_escape(str(uid_ret))}")
		if day or time_v:
			lines.append(f"<b>Created:</b> {html_escape(str(day))} {html_escape(str(time_v))}".strip())

		caption = "\n".join(lines) if lines else "No details."

		await update.message.reply_text(caption, parse_mode="HTML", disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# helper: split a long caption so photo caption stays <= max_photo_len
def split_caption(caption: str, max_photo_len: int = 900):
	"""
	Return a tuple (photo_caption, extra_text).
	If caption length <= max_photo_len -> extra_text is None.
	Otherwise photo_caption is first max_photo_len chars (try to cut at newline),
	and extra_text is the remainder.
	"""
	if not caption:
		return ("", None)
	if len(caption) <= max_photo_len:
		return (caption, None)
	# try to split at last newline before max_photo_len
	idx = caption.rfind("\n", 0, max_photo_len)
	if idx == -1:
		idx = max_photo_len
	photo_caption = caption[:idx].rstrip()
	extra_text = caption[idx:].lstrip()
	return (photo_caption, extra_text)


# helper: build TikTok post URL
def build_tiktok_post_url(unique_id: str, video_id: str) -> str:
	if not unique_id or not video_id:
		return ""
	return f"https://www.tiktok.com/@{unique_id}/video/{video_id}"


# /trendtt - trending videos
async def trendtt(update: Update, context: ContextTypes.DEFAULT_TYPE):
	api_url = "https://adidaphat.site/tiktok?type=trending"
	try:
		r = requests.get(api_url, timeout=20)
		j = r.json()
		items = j.get("data") or []
		if not items:
			await update.message.reply_text("❌ Không có kết quả trending.")
			return

		text_lines = []
		for it in items[:8]:
			title = it.get("title", "No title")
			author = it.get("author") or {}
			unique = author.get("unique_id") or author.get("uniqueId")
			video_id = it.get("video_id") or it.get("videoId")
			link = build_tiktok_post_url(unique, video_id) or (it.get("origin_cover") or it.get("cover") or "")
			text_lines.append(f"• <b>{title}</b>\n<a href='{link}'>{link}</a>")

		await update.message.reply_text("\n\n".join(text_lines), parse_mode="HTML", disable_web_page_preview=False)
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /tukhoatt <keywords> - search videos
async def tukhoatt(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /tukhoatt <từ khóa>")
		return

	keyword = " ".join(context.args)
	api_url = f"https://adidaphat.site/tiktok?type=searchvideo&keywords={keyword}"
	try:
		r = requests.get(api_url, timeout=20)
		j = r.json()
		data = j.get("data") or {}
		items = data.get("videos") if isinstance(data, dict) and data.get("videos") is not None else (data if isinstance(data, list) else [])
		if not items:
			await update.message.reply_text("❌ Không tìm thấy kết quả.")
			return

		text_lines = []
		for it in items[:8]:
			title = it.get("title", "No title")
			author = it.get("author") or {}
			unique = author.get("unique_id") or author.get("uniqueId")
			video_id = it.get("video_id") or it.get("videoId")
			link = build_tiktok_post_url(unique, video_id) or (it.get("origin_cover") or it.get("cover") or "")
			text_lines.append(f"• <b>{title}</b>\n<a href='{link}'>{link}</a>")

		await update.message.reply_text("\n\n".join(text_lines), parse_mode="HTML", disable_web_page_preview=False)
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /postusertt <username> - user posts (videos/images)
async def postusertt(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /postusertt <username>")
		return

	unique_id = context.args[0].lstrip("@").strip()
	api_url = f"https://adidaphat.site/tiktok?type=userposts&unique_id={unique_id}"
	try:
		r = requests.get(api_url, timeout=20)
		j = r.json()
		data = j.get("data") or {}
		items = data.get("videos") if isinstance(data, dict) and data.get("videos") is not None else (data if isinstance(data, list) else [])
		if not items:
			await update.message.reply_text("❌ Không tìm thấy bài đăng của user.")
			return

		text_lines = []
		for it in items[:8]:
			title = it.get("title", "No title")
			video_id = it.get("video_id") or it.get("videoId")
			link = build_tiktok_post_url(unique_id, video_id) or (it.get("origin_cover") or it.get("cover") or "")
			text_lines.append(f"• <b>{title}</b>\n<a href='{link}'>{link}</a>")

		await update.message.reply_text("\n\n".join(text_lines), parse_mode="HTML", disable_web_page_preview=False)
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /videofb <url> - download Facebook video (SD/HD)
async def videofb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /videofb <url>")
		return

	input_url = context.args[0].strip()
	api_url = f"https://adidaphat.site/facebook/video?url={input_url}"

	try:
		r = requests.get(api_url, timeout=25)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ API trả về không có dữ liệu hoặc URL không hợp lệ.")
			return

		orig = j.get("url") or input_url
		sd = j.get("sd")
		hd = j.get("hd")
		thumb = j.get("thumbnail") or j.get("thumb")

		buttons = []
		if hd:
			buttons.append([InlineKeyboardButton("▶️ HD", url=hd)])
		if sd:
			buttons.append([InlineKeyboardButton("▶️ SD", url=sd)])
		reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

		caption = f"<b>Facebook Video</b>\n{html_escape(orig)}"
		# send thumbnail if available, otherwise send text with links
		if thumb:
			photo_caption, extra = split_caption(caption)
			await update.message.reply_photo(photo=thumb, caption=photo_caption, parse_mode="HTML", reply_markup=reply_markup)
			if extra:
				await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
		else:
			await update.message.reply_text(caption, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=False)

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# /videoyt <url> - youtube download via adidaphat.site/dowall
async def videoyt(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /videoyt <url>")
		return

	input_url = context.args[0].strip()
	api_url = f"https://adidaphat.site/dowall?url={input_url}"

	try:
		r = requests.get(api_url, timeout=30)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ API không trả dữ liệu hoặc URL không hợp lệ.")
			return

		title = j.get("title") or ""
		thumb = j.get("thumbnail") or ""
		duration = j.get("duration") or ""
		medias = j.get("medias") or []

		buttons = []
		# show fewer buttons (max 6) to avoid "reply markup too long"
		for m in medias[:6]:
			murl = m.get("url")
			if not murl:
				continue
			label = m.get("quality") or m.get("extension") or "link"
			if len(label) > 30:
				label = label[:27] + "..."
			buttons.append([InlineKeyboardButton(label, url=murl)])

		# fallback: include original source link if no medias
		if j.get("url") and not any(btn for btn in buttons if btn):
			buttons.append([InlineKeyboardButton("Original", url=j.get("url"))])

		reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

		caption_lines = []
		if title:
			caption_lines.append(f"<b>{html_escape(title)}</b>")
		if duration:
			caption_lines.append(f"Duration: {html_escape(str(duration))}")
		caption = "\n".join(caption_lines) if caption_lines else "YouTube video"

		# Try sending with inline buttons; on failure (markup too long) fallback to text links
		try:
			if thumb:
				photo_caption, extra = split_caption(caption)
				await update.message.reply_photo(photo=thumb, caption=photo_caption, parse_mode="HTML", reply_markup=reply_markup)
				if extra:
					await update.message.reply_text(extra, parse_mode="HTML", disable_web_page_preview=False)
			else:
				await update.message.reply_text(caption, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=False)
		except Exception as e:
			err = str(e)
			if "Reply markup is too long" in err or "ReplyMarkup" in err:
				# Fallback: send plain text list of media links (up to 12)
				lines = []
				if title:
					lines.append(f"*{title}*")
				if duration:
					lines.append(f"Duration: {duration}")
				lines.append("")  # separator
				for i, m in enumerate(medias[:12], 1):
					murl = m.get("url")
					if not murl:
						continue
					label = m.get("quality") or m.get("extension") or f"link{i}"
					lines.append(f"{i}. {label}: {murl}")
				await update.message.reply_text("\n".join(lines), parse_mode=None, disable_web_page_preview=False)
			else:
				# re-raise or report other errors
				await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")


# helper: fetch API that may return JSON with 'url' or an image binary
def _fetch_image_or_json(api_url: str, timeout=30):
	r = requests.get(api_url, timeout=timeout)
	# try json first
	try:
		return r.json(), r
	except Exception:
		# not json, return (None, response) for raw image
		return None, r

# /xoanen <url>
async def xoanen(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /xoanen <url>")
		return
	img = context.args[0].strip()
	api_url = f"https://adidaphat.site/removebg?url={quote_plus(img)}"
	try:
		j, r = _fetch_image_or_json(api_url, timeout=30)
		if j:
			img_url = j.get("url") or j.get("image") or j.get("result")
			if img_url:
				await update.message.reply_photo(photo=img_url)
				return
		# raw image fallback
		ct = r.headers.get("content-type", "")
		if ct.startswith("image/"):
			await update.message.reply_photo(photo=r.content)
			return
		await update.message.reply_text("❌ Không nhận được ảnh từ API.")
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

# /doantuoi <url>
async def doantuoi(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /doantuoi <url>")
		return
	img = context.args[0].strip()
	api_url = f"https://adidaphat.site/doantuoi?url={quote_plus(img)}"
	try:
		r = requests.get(api_url, timeout=20)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ API không trả dữ liệu.")
			return
		if j.get("success"):
			age = j.get("age")
			msg = j.get("message") or ""
			await update.message.reply_text(f"Đoán tuổi: {age}\n{msg}")
		else:
			await update.message.reply_text(f"❌ API trả về lỗi: {j}")
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

# /sdt <number>
async def sdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /sdt <số điện thoại>")
		return
	number = context.args[0].strip()
	api_url = f"https://adidaphat.site/valuation?sdt={quote_plus(number)}"
	try:
		r = requests.get(api_url, timeout=15)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ API không trả dữ liệu.")
			return
		val_map = j.get("data", {}).get("valuation", {})
		val = val_map.get(number) or next(iter(val_map.values()), None)
		if val:
			await update.message.reply_text(f"Số: {number}\nGiá trị ước tính: {val}")
		else:
			await update.message.reply_text("❌ Không tìm thấy kết quả định giá.")
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

# /taoanhai <prompt>
async def taoanhai(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not context.args:
		await update.message.reply_text("❌ Dùng: /taoanhai <prompt>")
		return
	prompt = " ".join(context.args).strip()
	api_url = f"https://adidaphat.site/flux?prompt={quote_plus(prompt)}"
	try:
		r = requests.get(api_url, timeout=30)
		j = r.json() if r.status_code == 200 else {}
		if not j:
			await update.message.reply_text("❌ API không trả dữ liệu.")
			return
		if j.get("status") in ("success",) and j.get("url"):
			await update.message.reply_photo(photo=j.get("url"))
		else:
			# sometimes API may return direct image bytes
			ct = r.headers.get("content-type", "")
			if ct.startswith("image/"):
				await update.message.reply_photo(photo=r.content)
			else:
				await update.message.reply_text(f"❌ API trả về: {j}")
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

# helper to call QR APIs and send image result
async def _call_qr_and_send(api_url: str, update: Update):
	try:
		j, r = _fetch_image_or_json(api_url, timeout=25)
		if j:
			img_url = j.get("url") or j.get("image")
			if img_url:
				await update.message.reply_photo(photo=img_url)
				return
		ct = r.headers.get("content-type", "")
		if ct.startswith("image/"):
			await update.message.reply_photo(photo=r.content)
			return
		await update.message.reply_text("❌ API không trả ảnh QR.")
	except Exception as e:
		await update.message.reply_text(f"⚠️ Lỗi khi gọi API: {e}")

# /vcb <stk> <tien> <noidung> <ctk>
async def vcb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) < 4:
		await update.message.reply_text("❌ Dùng: /vcb <stk> <tien> <noidung> <chu_tk>")
		return
	stk = context.args[0].strip()
	tien = context.args[1].strip()
	ctk = context.args[-1].strip()
	noidung = " ".join(context.args[2:-1]).strip()
	api_url = f"https://adidaphat.site/vcb?stk={quote_plus(stk)}&tien={quote_plus(tien)}&noidung={quote_plus(noidung)}&ctk={quote_plus(ctk)}&apikey=apikeysumi"
	await _call_qr_and_send(api_url, update)

# /mb <stk> <tien> <noidung> <ctk>
async def mb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) < 4:
		await update.message.reply_text("❌ Dùng: /mb <stk> <tien> <noidung> <chu_tk>")
		return
	stk = context.args[0].strip()
	tien = context.args[1].strip()
	ctk = context.args[-1].strip()
	noidung = " ".join(context.args[2:-1]).strip()
	api_url = f"https://adidaphat.site/mb?stk={quote_plus(stk)}&tien={quote_plus(tien)}&noidung={quote_plus(noidung)}&ctk={quote_plus(ctk)}&apikey=apikeysumi"
	await _call_qr_and_send(api_url, update)

# /vtb <stk> <tien> <noidung> <ctk>
async def vtb(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) < 4:
		await update.message.reply_text("❌ Dùng: /vtb <stk> <tien> <noidung> <chu_tk>")
		return
	stk = context.args[0].strip()
	tien = context.args[1].strip()
	ctk = context.args[-1].strip()
	noidung = " ".join(context.args[2:-1]).strip()
	api_url = f"https://adidaphat.site/vtb?stk={quote_plus(stk)}&tien={quote_plus(tien)}&noidung={quote_plus(noidung)}&ctk={quote_plus(ctk)}&apikey=apikeysumi"
	await _call_qr_and_send(api_url, update)

# /momo <stk> <tien> <noidung>
async def momo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if len(context.args) < 3:
		await update.message.reply_text("❌ Dùng: /momo <stk> <tien> <noidung>")
		return
	stk = context.args[0].strip()
	tien = context.args[1].strip()
	noidung = " ".join(context.args[2:]).strip()
	api_url = f"https://adidaphat.site/momo?stk={quote_plus(stk)}&tien={quote_plus(tien)}&noidung={quote_plus(noidung)}&apikey=apikeysumi"
	await _call_qr_and_send(api_url, update)

# /time - hiện thời gian hoạt động bot
async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    uptime = int(now - BOT_START_TIME)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    seconds = uptime % 60
    msg = f"⏱ Bot đã hoạt động: {hours} giờ {minutes} phút {seconds} giây."
    await update.message.reply_text(msg)

# --- NEW: Key management helpers ---
def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def generate_key():
    return secrets.token_hex(8).upper()

def check_user_access(user_id: int) -> bool:
    keys_data = load_keys()
    now = datetime.now()
    for v in keys_data.values():
        if str(user_id) in v.get("users", []):
            try:
                expire_time = datetime.strptime(v.get("expire","1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                if now <= expire_time:
                    return True
            except Exception:
                continue
    return False

# Admin-only: remove admin id from all keys (useful to "xoá phần key với id admin")
async def clearkeyadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    admin_id = str(update.effective_user.id)
    keys_data = load_keys()
    removed = []
    for k, v in keys_data.items():
        if admin_id in v.get("users", []):
            v["users"] = [u for u in v.get("users", []) if u != admin_id]
            removed.append(k)
    save_keys(keys_data)
    if removed:
        await update.message.reply_text(f"✅ Đã xóa admin id khỏi các key: {', '.join(removed)}")
    else:
        await update.message.reply_text("⚠️ Không tìm thấy key nào chứa admin id.")

# Commands: taokey, listkey, xoakey, key, user
async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ Bạn không có quyền tạo key.")
        return
    if len(context.args) < 3:
        await update.message.reply_text("⚠️ Dùng: /taokey <số_lượng> <số_ngày> <số_giờ>")
        return
    try:
        count = int(context.args[0])
        days = int(context.args[1])
        hours = int(context.args[2])
    except ValueError:
        await update.message.reply_text("⚠️ Tham số phải là số nguyên.")
        return
    keys_data = load_keys()
    expire_time = (datetime.now() + timedelta(days=days, hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    new_keys = []
    for _ in range(count):
        key = generate_key()
        keys_data[key] = {"expire": expire_time, "users": []}
        new_keys.append(key)
    save_keys(keys_data)
    await update.message.reply_text(f"✅ Tạo {count} key thành công:\n" + "\n".join(new_keys))

async def list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    keys_data = load_keys()
    if not keys_data:
        await update.message.reply_text("⚠️ Chưa có key nào.")
        return
    text = "🔑 Danh sách key:\n"
    for k, v in keys_data.items():
        text += f"{k} | Hết hạn: {v.get('expire')} | Người dùng: {len(v.get('users',[]))}\n"
    await update.message.reply_text(text)

async def delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ Bạn không có quyền.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /xoakey <key>")
        return
    key = context.args[0]
    keys_data = load_keys()
    if key in keys_data:
        del keys_data[key]
        save_keys(keys_data)
        await update.message.reply_text(f"✅ Đã xóa key `{key}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Key không tồn tại.")

async def activate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /key <key>")
        return
    key = context.args[0]
    keys_data = load_keys()
    user_id = str(update.effective_user.id)
    if key not in keys_data:
        await update.message.reply_text("❌ Key không tồn tại.")
        return
    try:
        expire_time = datetime.strptime(keys_data[key]["expire"], "%Y-%m-%d %H:%M:%S")
    except Exception:
        await update.message.reply_text("⚠️ Định dạng thời hạn key không hợp lệ.")
        return
    if datetime.now() > expire_time:
        await update.message.reply_text("⚠️ Key đã hết hạn.")
        return
    if user_id not in keys_data[key].get("users", []):
        keys_data[key].setdefault("users", []).append(user_id)
        save_keys(keys_data)
    await update.message.reply_text(f"✅ Key `{key}` đã kích hoạt thành công!", parse_mode="Markdown")

async def count_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keys_data = load_keys()
    users = set()
    for v in keys_data.values():
        users.update(v.get("users", []))
    await update.message.reply_text(f"👥 Tổng số người dùng bot: {len(users)}")

async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👑 Admin bot:\n" + "\n".join([f"- {admin_id}" for admin_id in ADMINS])
    await update.message.reply_text(text)
# --- END Key management helpers ---

# --- NEW: sqlmap helpers ---
def clean_sqlmap_output(output: str) -> str:
    lines = output.splitlines()
    filtered = [line for line in lines if not re.search(r"\[INFO\] current status:", line)]
    return "\n".join(filtered)

def parse_sqlmap_output(output: str) -> str:
    explanation = ""
    dbms_match = re.search(r"back-end DBMS: (.+)", output)
    if dbms_match:
        explanation += f"• *Hệ quản trị CSDL:* `{dbms_match.group(1).strip()}`\n"

    banner_match = re.search(r"banner: '(.+)'", output)
    if banner_match:
        explanation += f"• *Phiên bản DBMS:* `{banner_match.group(1).strip()}`\n"

    tech_match = re.search(r"web application technology: (.+)", output)
    if tech_match:
        explanation += f"• *Công nghệ Website:* `{tech_match.group(1).strip()}`\n"

    db_list_match = re.search(r"available databases \[.+\]:\s*\n(.+?)(?=\n\n|\Z)", output, re.DOTALL)
    if db_list_match:
        databases = [db.replace('[*] ', '').strip() for db in db_list_match.group(1).split('\n') if db.strip()]
        explanation += f"• *Database khả dụng:* `{', '.join(databases)}`\n"

    if "Type: boolean-based blind" in output:
        explanation += "• *Lỗ hổng:* Boolean-based blind\n"
    if "Type: error-based" in output:
        explanation += "• *Lỗ hổng:* Error-based\n"
    if "Type: time-based blind" in output:
        explanation += "• *Lỗ hổng:* Time-based blind\n"

    if not explanation:
        return "Không tìm thấy thông tin chi tiết."
    return explanation

async def sqli_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Bạn chưa kích hoạt key.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Dùng: /sqli <URL>")
        return
    url = context.args[0]
    await update.message.reply_text(f"🔍 Đang quét SQLi: `{url}`", parse_mode='Markdown')
    try:
        command = shlex.split(f'sqlmap -u "{url}" --batch --random-agent --banner --dbs --disable-coloring')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=600)
        stdout = clean_sqlmap_output(stdout)
        if stdout.strip():
            explanation = parse_sqlmap_output(stdout)
            await update.message.reply_markdown(f"**Kết quả phân tích:**\n{explanation}")
        elif stderr.strip():
            await update.message.reply_text(f"Lỗi SQLmap:\n```\n{stderr}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text("Không tìm thấy lỗ hổng.")
    except FileNotFoundError:
        await update.message.reply_text("❌ Không tìm thấy lệnh sqlmap.")
    except subprocess.TimeoutExpired:
        process.kill()
        await update.message.reply_text("⏱ Hết thời gian quét (10 phút).")

async def sqli_dump(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Bạn chưa kích hoạt key.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Dùng: /dump <URL> <db_name>")
        return
    url = context.args[0]
    db_name = context.args[1]
    await update.message.reply_text(f"📂 Đang liệt kê bảng trong DB `{db_name}`...", parse_mode='Markdown')
    try:
        command = shlex.split(f'sqlmap -u "{url}" -D "{db_name}" --tables --batch --random-agent --disable-coloring')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=600)
        stdout = clean_sqlmap_output(stdout)
        if stderr.strip():
            await update.message.reply_text(f"Lỗi SQLmap:\n```\n{stderr}\n```", parse_mode='Markdown')
            return
        if not stdout.strip():
            await update.message.reply_text("⚠️ Không có dữ liệu trả về.")
            return
        await update.message.reply_text(f"```\n{stdout[:3800]}\n```", parse_mode='Markdown')
    except subprocess.TimeoutExpired:
        process.kill()
        await update.message.reply_text("⏱ Hết thời gian dump (10 phút).")

async def sqli_tables(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user_access(update.effective_user.id):
        await update.message.reply_text("❌ Bạn chưa kích hoạt key.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Dùng: /tables <URL> <db_name>")
        return
    url = context.args[0]
    db_name = context.args[1]
    await update.message.reply_text(f"📋 Đang liệt kê bảng của DB `{db_name}`...", parse_mode='Markdown')
    try:
        command = shlex.split(f'sqlmap -u "{url}" -D "{db_name}" --tables --batch --random-agent --disable-coloring')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=600)
        stdout = clean_sqlmap_output(stdout)
        if stderr.strip():
            await update.message.reply_text(f"Lỗi SQLmap:\n```\n{stderr}\n```", parse_mode='Markdown')
            return
        if stdout.strip():
            await update.message.reply_text(f"```\n{stdout[:3800]}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text("⚠️ Không tìm thấy bảng.")
    except subprocess.TimeoutExpired:
        process.kill()
        await update.message.reply_text("⏱ Hết thời gian liệt kê bảng.")
# --- END sqlmap helpers ---

# ============== MAIN ==============
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ...existing handlers...
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    # register md5 command
    app.add_handler(CommandHandler("md5", md5_cmd))
    # ...existing registrations...
    app.add_handler(CommandHandler("taokey", create_key))
    app.add_handler(CommandHandler("listkey", list_keys))
    app.add_handler(CommandHandler("xoakey", delete_key))
    app.add_handler(CommandHandler("key", activate_key))
    app.add_handler(CommandHandler("user", count_users))
    app.add_handler(CommandHandler("admin", show_admins))
    app.add_handler(CommandHandler("clearkeyadmin", clearkeyadmin))  # admin-only: remove admin id from keys

    # SQLMap commands
    app.add_handler(CommandHandler("sqli", sqli_check))
    app.add_handler(CommandHandler("dump", sqli_dump))
    app.add_handler(CommandHandler("tables", sqli_tables))

    # ...existing command registrations...
    app.add_handler(CommandHandler("taixvideos", taixvideos))
    app.add_handler(CommandHandler("timxvideos", timxvideos))
    app.add_handler(CommandHandler("taicliphot", taicliphot))
    app.add_handler(CommandHandler("timcliphot", timcliphot))
    app.add_handler(CommandHandler("infott", infott))
    app.add_handler(CommandHandler("taivideott", taivideott))
    # register new TikTok helpers
    app.add_handler(CommandHandler("trendtt", trendtt))
    app.add_handler(CommandHandler("tukhoatt", tukhoatt))
    app.add_handler(CommandHandler("postusertt", postusertt))
    # register new GitHub info command
    app.add_handler(CommandHandler("infogithub", infogithub))
    # register new Facebook info command
    app.add_handler(CommandHandler("infofb", infofb))
    app.add_handler(CommandHandler("timefb", timefb))  # added timefb
    app.add_handler(CommandHandler("videofb", videofb))  # added videofb
    app.add_handler(CommandHandler("videoyt", videoyt))  # added videoyt
    # register new commands
    app.add_handler(CommandHandler("xoanen", xoanen))
    app.add_handler(CommandHandler("doantuoi", doantuoi))
    app.add_handler(CommandHandler("sdt", sdt))
    app.add_handler(CommandHandler("taoanhai", taoanhai))
    app.add_handler(CommandHandler("vcb", vcb))
    app.add_handler(CommandHandler("mb", mb))
    app.add_handler(CommandHandler("vtb", vtb))
    app.add_handler(CommandHandler("momo", momo))
    # đăng ký lệnh /time (giữ lệnh hiện có)
    app.add_handler(CommandHandler("time", time_cmd))

    print("🚀 Bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()
