# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Games Module          ║
# ║  WordSeek | WordChain | Hangman          ║
# ║  Crossword | Wordle                      ║
# ╚══════════════════════════════════════════╝

import random
import string
from pyrogram import Client, filters
from pyrogram.types import Message
from core.translator import _

WORDS = [
    "apple","brave","chair","dance","eagle","flame","grape","heart","ivory","joker",
    "knife","lemon","maple","nerve","ocean","pearl","queen","river","storm","tiger",
    "ultra","vivid","water","xenon","yacht","zebra","amber","blaze","crane","drift",
    "elder","frost","globe","honey","infer","jazzy","kiosk","light","magic","night",
    "olive","piano","rouge","shade","torch","union","vault","witch","yield","zonal"
]
WORDS5 = [w for w in WORDS if len(w) == 5]

# ── In-memory game state ──────────────────────
ws_games: dict  = {}   # wordseek
wc_games: dict  = {}   # wordchain
hm_games: dict  = {}   # hangman
wd_games: dict  = {}   # wordle
cw_games: dict  = {}   # crossword
stats:    dict  = {}   # {(chat_id,user_id): {game: {played,won}}}
purge_from: dict = {}  # for wordseek


def _upd_stats(cid, uid, game, won):
    k = (cid, uid)
    stats.setdefault(k, {}).setdefault(game, {"played": 0, "won": 0})
    stats[k][game]["played"] += 1
    if won:
        stats[k][game]["won"] += 1


def _get_stats(cid, uid, game):
    d = stats.get((cid, uid), {}).get(game, {"played": 0, "won": 0})
    return d["played"], d["won"]


# ════════════════════════════════════════════
#  🔎 WORD SEEK
# ════════════════════════════════════════════

def _make_grid(words, size=8):
    grid = [[random.choice(string.ascii_lowercase) for _ in range(size)] for _ in range(size)]
    placed = []
    for w in words[:4]:
        if len(w) <= size:
            r, c = random.randint(0, size-1), random.randint(0, size-len(w))
            for i, ch in enumerate(w):
                grid[r][c+i] = ch
            placed.append(w)
    return "\n".join(" ".join(row).upper() for row in grid), placed


@Client.on_message(filters.command("wordseek") & filters.group)
async def cmd_wordseek(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 1)
    sub = args[1].lower() if len(args) > 1 else ""

    if sub == "stop":
        ws_games.pop(cid, None)
        return await message.reply(await _(cid, "games.wordseek_stopped"))
    if sub == "stats":
        p, w = _get_stats(cid, message.from_user.id, "wordseek")
        return await message.reply(await _(cid, "games.stats", game="Word Seek", played=p, won=w))
    if sub == "hint" and cid in ws_games:
        g = ws_games[cid]
        rem = [w for w in g["words"] if w not in g["found"]]
        if rem:
            hw = rem[0]
            return await message.reply(f"💡 One word starts with **{hw[0].upper()}** and has **{len(hw)}** letters.")
    if sub == "skip" and cid in ws_games:
        ws_games.pop(cid, None)
        return await message.reply(await _(cid, "games.wordseek_skipped"))
    if sub == "answer" and cid in ws_games:
        g = ws_games.pop(cid)
        return await message.reply(await _(cid, "games.wordseek_answer", words=", ".join(g["words"]).upper()))

    words = random.sample(WORDS, 4)
    grid, placed = _make_grid(words)
    ws_games[cid] = {"words": placed, "found": []}
    await message.reply(await _(cid, "games.wordseek_start", count=len(placed), grid=grid))


@Client.on_message(filters.group & filters.text & ~filters.command(""))
async def _ws_checker(client: Client, message: Message):
    cid = message.chat.id
    if cid not in ws_games:
        return
    g = ws_games[cid]
    word = message.text.strip().lower()
    if word in g["words"] and word not in g["found"]:
        g["found"].append(word)
        _upd_stats(cid, message.from_user.id, "wordseek", False)
        rem = len(g["words"]) - len(g["found"])
        if rem == 0:
            ws_games.pop(cid)
            _upd_stats(cid, message.from_user.id, "wordseek", True)
            return await message.reply(await _(cid, "games.wordseek_win", name=message.from_user.mention))
        await message.reply(await _(cid, "games.wordseek_found", word=word.upper(), remaining=rem))


# ════════════════════════════════════════════
#  🔗 WORD CHAIN
# ════════════════════════════════════════════

@Client.on_message(filters.command("wordchain") & filters.group)
async def cmd_wordchain(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 1)
    sub = args[1].lower() if len(args) > 1 else ""

    if sub == "stop":
        wc_games.pop(cid, None)
        return await message.reply(await _(cid, "games.wordchain_stopped"))
    if sub == "stats":
        p, w = _get_stats(cid, message.from_user.id, "wordchain")
        return await message.reply(await _(cid, "games.stats", game="Word Chain", played=p, won=w))
    if sub == "rules":
        return await message.reply(
            "📖 **Word Chain Rules:**\n\n"
            "Each word must start with the last letter of the previous word.\n"
            "No repeating words!\n"
            "Example: Apple → Elephant → Tiger → Rabbit → Tree"
        )
    if sub == "skip" and cid in wc_games:
        g = wc_games[cid]
        nw = next((w for w in WORDS if w[0] == g["last"]), random.choice(WORDS))
        g["last"] = nw[-1]
        g["used"].add(nw)
        return await message.reply(await _(cid, "games.wordchain_next", word=nw.upper(), letter=nw[-1].upper()))

    sw = random.choice(WORDS)
    wc_games[cid] = {"last": sw[-1], "used": {sw}}
    await message.reply(await _(cid, "games.wordchain_start", word=sw.upper(), letter=sw[-1].upper()))


@Client.on_message(filters.group & filters.text & ~filters.command(""))
async def _wc_checker(client: Client, message: Message):
    cid = message.chat.id
    if cid not in wc_games:
        return
    g = wc_games[cid]
    word = message.text.strip().lower()
    if not word.isalpha() or len(word) < 2:
        return
    if word[0] != g["last"]:
        return
    if word in g["used"]:
        return await message.reply(await _(cid, "games.wordchain_used", word=word.upper()))
    g["used"].add(word)
    g["last"] = word[-1]
    _upd_stats(cid, message.from_user.id, "wordchain", True)
    await message.reply(await _(cid, "games.wordchain_next", word=word.upper(), letter=word[-1].upper()))


# ════════════════════════════════════════════
#  🙈 HANGMAN
# ════════════════════════════════════════════

STAGES = [
    "```\n  +---+\n  |   |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n=========```",
]


def _hm_display(g):
    word = g["word"]
    guessed = g["guessed"]
    disp = " ".join(ch.upper() if ch in guessed else "_" for ch in word)
    wrong = [ch for ch in guessed if ch not in word]
    stage = STAGES[min(len(wrong), 6)]
    return f"{stage}\nWord: **{disp}**\nWrong ({len(wrong)}/6): **{', '.join(wrong).upper() or 'None'}**"


@Client.on_message(filters.command("hangman") & filters.group)
async def cmd_hangman(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 1)
    sub = args[1].lower() if len(args) > 1 else ""

    if sub == "stop":
        hm_games.pop(cid, None)
        return await message.reply(await _(cid, "games.hangman_stopped"))
    if sub == "stats":
        p, w = _get_stats(cid, message.from_user.id, "hangman")
        return await message.reply(await _(cid, "games.stats", game="Hangman", played=p, won=w))
    if sub == "hint" and cid in hm_games:
        g = hm_games[cid]
        unguessed = [ch for ch in g["word"] if ch not in g["guessed"]]
        if unguessed:
            r = random.choice(unguessed)
            g["guessed"].add(r)
            return await message.reply(f"💡 Hint: **{r.upper()}** revealed!\n\n{_hm_display(g)}")

    word = random.choice(WORDS)
    hm_games[cid] = {"word": word, "guessed": set()}
    await message.reply(await _(cid, "games.hangman_start", display=_hm_display(hm_games[cid])))


@Client.on_message(filters.command("guess") & filters.group)
async def cmd_guess(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 1)

    # Wordle guess
    if cid in wd_games:
        if len(args) < 2:
            return await message.reply("Usage: `/guess <5-letter-word>`")
        guess = args[1].lower().strip()
        if len(guess) != 5 or not guess.isalpha():
            return await message.reply("❌ Valid 5-letter word only!")
        g = wd_games[cid]
        result = _wordle_check(g["word"], guess)
        g["attempts"].append(result)
        board = "\n".join(g["attempts"])
        if guess == g["word"]:
            wd_games.pop(cid)
            _upd_stats(cid, message.from_user.id, "wordle", True)
            return await message.reply(await _(cid, "games.wordle_win",
                                               name=message.from_user.mention,
                                               attempts=len(g["attempts"]), board=board))
        if len(g["attempts"]) >= 6:
            w = wd_games.pop(cid)["word"]
            _upd_stats(cid, message.from_user.id, "wordle", False)
            return await message.reply(await _(cid, "games.wordle_lose", word=w.upper(), board=board))
        rem = 6 - len(g["attempts"])
        return await message.reply(f"{board}\n\n{rem} attempt(s) left.")

    # Hangman guess
    if cid in hm_games:
        if len(args) < 2 or len(args[1]) != 1:
            return await message.reply("Usage: `/guess <letter>`")
        letter = args[1].lower()
        g = hm_games[cid]
        if letter in g["guessed"]:
            return await message.reply(f"❌ **{letter.upper()}** already guessed!")
        g["guessed"].add(letter)
        wrong = [ch for ch in g["guessed"] if ch not in g["word"]]
        display = _hm_display(g)
        if all(ch in g["guessed"] for ch in g["word"]):
            hm_games.pop(cid)
            _upd_stats(cid, message.from_user.id, "hangman", True)
            return await message.reply(await _(cid, "games.hangman_win",
                                               name=message.from_user.mention,
                                               word=g["word"].upper()) + f"\n\n{display}")
        if len(wrong) >= 6:
            w = hm_games.pop(cid)["word"]
            _upd_stats(cid, message.from_user.id, "hangman", False)
            return await message.reply(await _(cid, "games.hangman_lose", word=w.upper()) + f"\n\n{display}")
        return await message.reply(display)

    await message.reply(await _(cid, "games.no_game"))


@Client.on_message(filters.command("solve") & filters.group)
async def cmd_solve(client: Client, message: Message):
    cid = message.chat.id
    if cid not in hm_games:
        return await message.reply(await _(cid, "games.no_game"))
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/solve <word>`")
    g = hm_games[cid]
    if args[1].lower().strip() == g["word"]:
        hm_games.pop(cid)
        _upd_stats(cid, message.from_user.id, "hangman", True)
        await message.reply(await _(cid, "games.hangman_win",
                                    name=message.from_user.mention, word=g["word"].upper()))
    else:
        await message.reply(f"❌ **{args[1].upper()}** is wrong! Keep guessing!")


# ════════════════════════════════════════════
#  🟩 WORDLE
# ════════════════════════════════════════════

def _wordle_check(secret, guess):
    result = []
    for i, ch in enumerate(guess):
        if ch == secret[i]:
            result.append("🟩")
        elif ch in secret:
            result.append("🟨")
        else:
            result.append("⬜")
    return " ".join(result) + f"  `{guess.upper()}`"


@Client.on_message(filters.command("wordle") & filters.group)
async def cmd_wordle(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 1)
    sub = args[1].lower() if len(args) > 1 else ""

    if sub == "stop":
        wd_games.pop(cid, None)
        return await message.reply(await _(cid, "games.wordle_stopped"))
    if sub == "stats":
        p, w = _get_stats(cid, message.from_user.id, "wordle")
        return await message.reply(await _(cid, "games.stats", game="Wordle", played=p, won=w))
    if sub == "answer" and cid in wd_games:
        w = wd_games.pop(cid)["word"]
        return await message.reply(f"📖 The word was: **{w.upper()}**")
    if sub == "hint" and cid in wd_games:
        w = wd_games[cid]["word"]
        return await message.reply(f"💡 The word contains **{random.choice(w).upper()}**")
    if sub == "skip" and cid in wd_games:
        w = wd_games.pop(cid)["word"]
        return await message.reply(f"⏭ Skipped! Word was **{w.upper()}**")

    word = random.choice(WORDS5)
    wd_games[cid] = {"word": word, "attempts": []}
    await message.reply(await _(cid, "games.wordle_start"))


# ════════════════════════════════════════════
#  🧩 CROSSWORD
# ════════════════════════════════════════════

CW_DATA = [
    {"1 Across": ("A red fruit 🍎", "apple"),
     "2 Down":   ("Opposite of night", "day"),
     "3 Across": ("Large body of water", "ocean")},
    {"1 Across": ("King of the jungle 🦁", "lion"),
     "2 Down":   ("Water falls from sky as...", "rain"),
     "3 Across": ("You read this 📖", "book")},
    {"1 Across": ("Frozen water ❄️", "ice"),
     "2 Down":   ("Opposite of cold", "hot"),
     "3 Across": ("A bright star ⭐", "star")},
]


@Client.on_message(filters.command("crossword") & filters.group)
async def cmd_crossword(client: Client, message: Message):
    cid = message.chat.id
    args = message.text.split(None, 2)
    sub = args[1].lower() if len(args) > 1 else ""

    if sub == "stop":
        cw_games.pop(cid, None)
        return await message.reply(await _(cid, "games.crossword_stopped"))
    if sub == "stats":
        p, w = _get_stats(cid, message.from_user.id, "crossword")
        return await message.reply(await _(cid, "games.stats", game="Crossword", played=p, won=w))
    if sub == "skip":
        cw_games.pop(cid, None)
        return await message.reply(await _(cid, "games.crossword_stopped"))
    if sub == "hint" and cid in cw_games and len(args) > 2:
        g = cw_games[cid]
        for key, (clue, ans) in g["clues"].items():
            if args[2].strip() in key:
                return await message.reply(f"💡 **{key}** hint: First letter is **{ans[0].upper()}**")

    data = random.choice(CW_DATA)
    cw_games[cid] = {"clues": data, "answered": {}}
    clue_text = "\n".join(f"**{k}:** {v[0]}" for k, v in data.items())
    await message.reply(await _(cid, "games.crossword_start", clues=clue_text))


@Client.on_message(filters.command("answer") & filters.group)
async def cmd_crossword_answer(client: Client, message: Message):
    cid = message.chat.id
    if cid not in cw_games:
        return await message.reply(await _(cid, "games.no_game"))
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply("Usage: `/answer <number> <word>`")
    num, guess = args[1], args[2].lower().strip()
    g = cw_games[cid]
    matched = next((k for k in g["clues"] if num in k), None)
    if not matched:
        return await message.reply(f"❌ Clue **{num}** not found.")
    _, correct = g["clues"][matched]
    if guess == correct:
        g["answered"][matched] = True
        await message.reply(await _(cid, "games.crossword_correct", clue=matched, word=correct.upper()))
        if len(g["answered"]) == len(g["clues"]):
            cw_games.pop(cid)
            _upd_stats(cid, message.from_user.id, "crossword", True)
            await message.reply(await _(cid, "games.crossword_win", name=message.from_user.mention))
    else:
        await message.reply(await _(cid, "games.crossword_wrong", clue=matched))
