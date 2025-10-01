import os
import requests
import logging
import re
from urllib.parse import urlsplit, urlunsplit, unquote, quote_plus
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ============== CONFIG ==============
BOT_TOKEN = "7810405245:AAEvgzgKIunIT57vb-qa7ETHQ3x91XGCSOc"   # 🔑 Thay bằng token từ BotFather

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


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(
		"Xin chào 👋\n\n"
		"Tôi hỗ trợ các lệnh sau (nhóm theo dịch vụ):\n\n"
		"— Tổng quan —\n"
		"🔸 /start — Hiện trợ giúp\n"
		"🔸 /help  — Xem hướng dẫn (alias của /start)\n\n"
		"— Xvideos —\n"
		"📥 /taixvideos <url>\n"
		"    → Lấy link tải mp4 từ Xvideos\n"
		"🔍 /timxvideos <từ khóa>\n"
		"    → Tìm video trên Xvideos\n\n"
		"— ClipHot —\n"
		"📥 /taicliphot <url>\n"
		"    → Lấy link tải mp4 từ ClipHot\n"
		"🔍 /timcliphot <từ khóa>\n"
		"    → Tìm video trên ClipHot\n\n"
		"— TikTok —\n"
		"🔍 /infott <username>\n"
		"    → Thông tin user TikTok\n"
		"📥 /taivideott <url>\n"
		"    → Tải video TikTok (trả link HD / NoWM / WM)\n"
		"🔎 /trendtt\n"
		"    → Danh sách trending TikTok\n"
		"🔎 /tukhoatt <từ khóa>\n"
		"    → Tìm video TikTok theo từ khóa\n"
		"👤 /postusertt <username>\n"
		"    → Lấy bài đăng (video/ảnh) của user TikTok\n\n"
		"— GitHub —\n"
		"🔍 /infogithub <username>\n"
		"    → Thông tin user GitHub (login, repos, followers...)\n\n"
		"— Facebook —\n"
		"🔍 /infofb <uid>\n"
		"    → Thông tin tài khoản Facebook (sử dụng API)\n"
		"⏱ /timefb <uid>\n"
		"    → Thời gian tạo tài khoản Facebook (ngày & giờ)\n"
		"🎬 /videofb <url>\n"
		"    → Tải video Facebook (trả link HD/SD)\n\n"
		"— YouTube —\n"
		"🎥 /videoyt <url>\n"
		"    → Tải video YouTube (trả các bản chất lượng/âm thanh)\n\n"
		"— Hình ảnh & tiện ích —\n"
		"🖼 /xoanen <url>         → Xóa nền ảnh (removebg API)\n"
		"🧓 /doantuoi <url>       → Đoán tuổi từ ảnh\n"
		"☎️ /sdt <số>            → Định giá số điện thoại\n"
		"🖌 /taoanhai <prompt>    → Tạo ảnh AI từ prompt\n"
		"🏧 /vcb <stk> <tien> <noidung> <ctk> → QR chuyển khoản Vietcombank\n"
		"🏧 /mb  <stk> <tien> <noidung> <ctk> → QR chuyển khoản MB\n"
		"🏧 /vtb <stk> <tien> <noidung> <ctk> → QR chuyển khoản VTB\n"
		"📲 /momo <stk> <tien> <noidung>      → QR chuyển khoản MoMo\n\n"
		"Ví dụ nhanh:\n"
		"• /xoanen https://.../image.jpg\n"
		"• /doantuoi https://.../face.jpg\n"
		"• /sdt 0367894789\n"
		"• /taoanhai \"một con rồng màu xanh trên nền biển\"\n"
		"• /vcb 0123456789 100000 \"Nội dung\" \"Chủ tài khoản\"\n\n"
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


# add quote_plus import
from urllib.parse import urlsplit, urlunsplit, unquote, quote_plus

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

# ============== MAIN ==============
def main():
	app = ApplicationBuilder().token(BOT_TOKEN).build()

	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help_cmd))
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

	print("🚀 Bot đang chạy...")
	app.run_polling()


if __name__ == "__main__":
    main()