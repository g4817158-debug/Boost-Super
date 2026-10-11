import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton as Btn,
    InlineKeyboardMarkup as Markup,
    BotCommand,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

# =====================================================================
# CONFIG  (edit these)
# =====================================================================
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Payment wallets (set as Railway variables)
PAY_SOL = os.getenv("PAY_SOL", "SET_YOUR_SOL_ADDRESS")
PAY_EVM = os.getenv("PAY_EVM", "SET_YOUR_EVM_ADDRESS")  # ETH/BASE/BSC/HOOD/ARC

BRAND_HANDLE = "YourBrand"
DISCLAIMER_HANDLE = "YourBrandHub"
VOLUME_URL = "https://t.me/YourVolumeBot"
FEEDBACK_URL = "https://t.me/YourFeedbackBot"
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/YourSupport")

CALL_CHANNEL = "YourCallChannel"      # "Call, X & AMA with Pin @..."
JUNGLE_CHANNEL = "YourJungleChannel"  # "Call @..."
MASS_DM_REACH = "600K+"

# Trending prices: (duration, prime_price, ultra_price)
# ETH / BSC / ARC come from your screenshots.
# SOL / BASE / HOOD are PLACEHOLDERS - edit them.
ETH_PRICES = [
    ("4h", "0.10", "0.15"),
    ("8h", "0.14", "0.20"),
    ("12h", "0.18", "0.25"),
    ("24h", "0.26", "0.32"),
]

CHAINS = {
    "sol": {
        "label": "◎ SOL", "currency": "SOL", "handle": "YourSolTrending",
        "pay": PAY_SOL,
        "prices": [  # PLACEHOLDER
            ("4h", "1.00", "1.50"),
            ("8h", "1.40", "2.00"),
            ("12h", "1.80", "2.50"),
            ("24h", "2.60", "3.20"),
        ],
    },
    "eth": {
        "label": "🔷 ETH", "currency": "ETH", "handle": "MajorEthTrending",
        "pay": PAY_EVM, "prices": ETH_PRICES,
    },
    "base": {
        "label": "🔵 BASE", "currency": "ETH", "handle": "YourBaseTrending",
        "pay": PAY_EVM, "prices": ETH_PRICES,  # PLACEHOLDER (copied from ETH)
    },
    "bsc": {
        "label": "🟡 BSC", "currency": "BNB", "handle": "MajorBscTrending",
        "pay": PAY_EVM,
        "prices": [
            ("4h", "0.28", "0.42"),
            ("8h", "0.38", "0.52"),
            ("12h", "0.48", "0.62"),
            ("24h", "0.68", "0.82"),
        ],
    },
    "hood": {
        "label": "🍃 HOOD", "currency": "ETH", "handle": "YourHoodTrending",
        "pay": PAY_EVM, "prices": ETH_PRICES,  # PLACEHOLDER (copied from ETH)
    },
    "arc": {
        "label": "🔺 ARC", "currency": "USDC", "handle": "MajorARCTrending",
        "pay": PAY_EVM,
        "prices": [
            ("4h", "240.00", "370.00"),
            ("8h", "340.00", "490.00"),
            ("12h", "440.00", "610.00"),
            ("24h", "630.00", "780.00"),
        ],
    },
}

# Major Ultimate Boost packs (PLACEHOLDER prices, paid in USDC)
ULTIMATE = {
    "gold": {"name": "GOLD PACK", "price": "500.00"},
    "platinum": {"name": "PLATINUM PACK", "price": "1200.00"},
}
ULTIMATE_CURRENCY = "USDC"
ULTIMATE_PAY = PAY_EVM

FREE_BOOSTS = {
    "bumps": "Free Bumps",
    "mm": "Free Market Maker",
    "holders": "Free Holders",
    "none": "No Boost",
}

# =====================================================================
# TEXTS
# =====================================================================
HOME_TEXT = (
    f"🪙 <b>Boost your token!</b> @{BRAND_HANDLE}\n\n"
    "🆕 <b>New Trending Packages:</b>\n"
    "<i>Includes Button AD and Mass DM to reach all BuyBot users.</i>\n\n"
    "🎀 <b>Free Bumps, Market Maker or Holders</b>\n"
    "<i>Included with every Trending Ticket (SOL Chain only).</i>\n\n"
    f"⚠️ <b>Disclaimer:</b> @{DISCLAIMER_HANDLE}"
)

TRENDING_TEXT = (
    "🔘 <b>Button AD included</b>\n"
    "<i>Every Trending Ticket comes with a guaranteed Button AD placement.</i>\n\n"
    "💬 <b>Mass DM (optional)</b>\n"
    f"<i>Reach over {MASS_DM_REACH} BuyBot users with an additional Mass DM "
    "push to maximize exposure.</i>\n\n"
    "🎀 <b>Free Bumps, Market Maker or Holders!</b>\n"
    "<i>Every Trending includes extra support to fuel your momentum "
    "(SOL Chain only).</i>\n\n"
    "➡️ <b>Choose your chain:</b>"
)

BOOST_TEXT = (
    "🎀 <b>Choose your FREE Boost!</b>\n\n"
    "As a bonus, you can select <b>one free boost</b> to give your project "
    "an extra push.\n\n"
    "🎀 <b>Pick one of the following:</b>"
)

ADS_TEXT = (
    "🪙 <b>Exclusive Ads – High Impact Promotion for Your Project</b>\n\n"
    "🔥 <i>Reach thousands of real users with our top tier ad options "
    "across the Major ecosystem.</i>\n\n"
    "⚡ <i>Choose one of the options below to learn more and boost your "
    "project visibility.</i>"
)

ULTIMATE_TEXT = (
    "🪙 <b>Major Ultimate Boost</b>\n\n"
    "⭐ Maximum reach guaranteed! For ambitious tokens and presales, we "
    "offer an all-in-one package for maximum reach. By choosing one of our "
    "packages, you save a lot of money and, most importantly, time when it "
    "comes to organization. We have put together two packages for you.\n\n"
    "🔥 <b>GOLD PACK</b>\n"
    "✅ 24h Join Requirement\n"
    "✅ 1 Mass DM\n"
    "✅ 1 Day Button Ad\n"
    "✅ Major AMA\n"
    "✅ 24h Trending (Top 3)\n"
    f"✅ Call, X &amp; AMA with Pin @{CALL_CHANNEL}\n"
    f"✅ Call @{JUNGLE_CHANNEL}\n\n"
    "🔥 <b>PLATINUM PACK</b>\n"
    "✅ 72h Join Requirement\n"
    "✅ 2 Mass DM\n"
    "✅ Major AMA\n"
    "✅ 72h Trending (Top 3)\n"
    f"✅ Call, X &amp; AMA @{CALL_CHANNEL}\n"
    f"✅ Call @{JUNGLE_CHANNEL}\n\n"
    "❗ <b>Contact us for more info!</b>"
)


def prices_text(chain: dict) -> str:
    return (
        "🥇 <b>Prime</b>\n"
        "<b>• Button Ad (all Groups)</b>\n"
        f"<b>• Listing on @{chain['handle']}</b>\n"
        "<b>• Guaranteed Top10</b>\n\n"
        "💎 <b>Ultra</b>\n"
        "<b>• Everything in Prime</b>\n"
        f"<b>• Mass DM to {MASS_DM_REACH} BuyBot users</b>\n\n"
        "🔥 <i>Paid trendings rank first.\n"
        "Longer duration = higher position.</i>"
    )


# =====================================================================
# KEYBOARDS
# =====================================================================
def home_kb():
    return Markup([
        [Btn("⚡ Trending", callback_data="trending"),
         Btn("💰 Volume", url=VOLUME_URL)],
        [Btn("📢 Exclusive Ads", callback_data="ads")],
        [Btn("🗳 Voting Boost", callback_data="soon"),
         Btn("🎁 Free Tools", callback_data="soon")],
        [Btn("✏️ Feedback", url=FEEDBACK_URL),
         Btn("💬 Support", url=SUPPORT_URL)],
    ])


def trending_kb():
    keys = list(CHAINS.keys())
    rows = []
    for i in range(0, len(keys), 2):
        rows.append([
            Btn(CHAINS[k]["label"], callback_data=f"chain:{k}")
            for k in keys[i:i + 2]
        ])
    rows.append([Btn("Back", callback_data="home")])
    return Markup(rows)


def boost_kb():
    return Markup([
        [Btn("⚡ Free Bumps", callback_data="boost:bumps"),
         Btn("📊 Free Market Maker", callback_data="boost:mm")],
        [Btn("👥 Free Holders", callback_data="boost:holders"),
         Btn("❌ No Boost", callback_data="boost:none")],
        [Btn("Back", callback_data="trending")],
    ])


def prices_kb(chain_key: str):
    chain = CHAINS[chain_key]
    cur = chain["currency"]
    rows = [[Btn("⬇️ PRIME", callback_data="noop"),
             Btn("⬇️ ULTRA", callback_data="noop")]]
    for i, (dur, prime, ultra) in enumerate(chain["prices"]):
        rows.append([
            Btn(f"{dur} | {prime} {cur}", callback_data=f"buy:{chain_key}:p:{i}"),
            Btn(f"{dur} | {ultra} {cur}", callback_data=f"buy:{chain_key}:u:{i}"),
        ])
    back = "chain:sol" if chain_key == "sol" else "trending"
    rows.append([Btn("Back", callback_data=back)])
    return Markup(rows)


def ads_kb():
    return Markup([
        [Btn("⭐ Major Ultimate Boost", callback_data="ub")],
        [Btn("🔥 Join2Vote", callback_data="soon")],
        [Btn("💬 Mass DM", callback_data="soon"),
         Btn("🎯 Button Ads", callback_data="soon")],
        [Btn("📣 Major AMA", callback_data="soon"),
         Btn("Back", callback_data="home")],
    ])


def ultimate_kb():
    cur = ULTIMATE_CURRENCY
    return Markup([
        [Btn("⬇️ GOLD", callback_data="noop"),
         Btn("⬇️ PLATINUM", callback_data="noop")],
        [Btn(f"{ULTIMATE['gold']['price']} {cur}", callback_data="ubbuy:gold"),
         Btn(f"{ULTIMATE['platinum']['price']} {cur}", callback_data="ubbuy:platinum")],
        [Btn("Back", callback_data="ads")],
    ])


def order_kb(back_data: str):
    return Markup([
        [Btn("💬 Contact Support", url=SUPPORT_URL)],
        [Btn("Back", callback_data=back_data)],
    ])


# =====================================================================
# HELPERS
# =====================================================================
async def show(query, text, kb):
    try:
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
            disable_web_page_preview=True,
        )
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


def order_text(lines: list[str], amount: str, currency: str, address: str) -> str:
    body = "\n".join(lines)
    return (
        "🧾 <b>Order Summary</b>\n\n"
        f"{body}\n\n"
        f"💳 Send exactly <b>{amount} {currency}</b> to:\n"
        f"<code>{address}</code>\n\n"
        "<i>After paying, contact support with your transaction hash and "
        "token address.</i>"
    )


# =====================================================================
# HANDLERS
# =====================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        HOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=home_kb(),
        disable_web_page_preview=True,
    )


async def trending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TRENDING_TEXT, parse_mode=ParseMode.HTML, reply_markup=trending_kb()
    )


async def ads_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        ADS_TEXT, parse_mode=ParseMode.HTML, reply_markup=ads_kb()
    )


async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Need help? Tap below.",
        reply_markup=Markup([[Btn("💬 Support", url=SUPPORT_URL)]]),
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    if data == "noop":
        await q.answer()
        return
    if data == "soon":
        await q.answer("Coming soon.", show_alert=True)
        return
    await q.answer()

    if data == "home":
        context.user_data.clear()
        await show(q, HOME_TEXT, home_kb())

    elif data == "trending":
        await show(q, TRENDING_TEXT, trending_kb())

    elif data == "ads":
        await show(q, ADS_TEXT, ads_kb())

    elif data.startswith("chain:"):
        key = data.split(":")[1]
        context.user_data["chain"] = key
        if key == "sol":
            await show(q, BOOST_TEXT, boost_kb())  # free boost is SOL only
        else:
            await show(q, prices_text(CHAINS[key]), prices_kb(key))

    elif data.startswith("boost:"):
        context.user_data["boost"] = data.split(":")[1]
        await show(q, prices_text(CHAINS["sol"]), prices_kb("sol"))

    elif data.startswith("buy:"):
        _, key, tier, idx = data.split(":")
        chain = CHAINS[key]
        dur, prime, ultra = chain["prices"][int(idx)]
        is_prime = tier == "p"
        price = prime if is_prime else ultra
        lines = [
            f"Chain: <b>{key.upper()}</b>",
            f"Package: <b>{'Prime' if is_prime else 'Ultra'}</b>",
            f"Duration: <b>{dur}</b>",
        ]
        if key == "sol":
            boost = FREE_BOOSTS.get(context.user_data.get("boost", "none"))
            lines.append(f"Free boost: <b>{boost}</b>")
        await show(
            q,
            order_text(lines, price, chain["currency"], chain["pay"]),
            order_kb(f"chain:{key}" if key != "sol" else "prices:sol"),
        )

    elif data == "prices:sol":
        await show(q, prices_text(CHAINS["sol"]), prices_kb("sol"))

    elif data == "ub":
        await show(q, ULTIMATE_TEXT, ultimate_kb())

    elif data.startswith("ubbuy:"):
        pack = ULTIMATE[data.split(":")[1]]
        lines = [
            "Package: <b>Major Ultimate Boost</b>",
            f"Pack: <b>{pack['name']}</b>",
        ]
        await show(
            q,
            order_text(lines, pack["price"], ULTIMATE_CURRENCY, ULTIMATE_PAY),
            order_kb("ub"),
        )


async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Main menu"),
        BotCommand("trending", "Trending packages"),
        BotCommand("ads", "Exclusive ads"),
        BotCommand("support", "Contact support"),
    ])


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trending", trending_cmd))
    app.add_handler(CommandHandler("ads", ads_cmd))
    app.add_handler(CommandHandler("support", support_cmd))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
