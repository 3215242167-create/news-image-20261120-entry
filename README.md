[![make.fun bounty](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/3215242167-create/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/3215242167-create/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120)

# The World Today — 20 November 2026 in one image

A newspaper front page summing up Friday 20 November 2026's world news, for make.fun's [Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120) bounty ($250 in USDC, 50 places paid).

## The image

`entry.png` (1024×1024, PNG) is drawn entirely by `main.py` (Python + PIL, Noto fonts bundled under `fonts/` so the render is identical in any sandbox) from headlines of the 20 November 2026 news cycle — no generated imagery, no AI-written text in the picture itself. Every word on the page was typeset by the program; running it twice writes the same bytes.

**Lead story — Shenzhen:** Trump, Xi and Putin hold the first-ever three-way talks at the APEC summit, issuing a joint declaration to reform the UN, cut nuclear risks and boost oil output — but no breakthrough on Ukraine or Iran. *(USA Today, CNN, Le Monde)*

**Also on the page:**
- The ICJ rules Myanmar committed genocide against the Rohingya in the 2017 crackdown — the first time the court has held a state responsible — and orders reparations. *(Reuters, BBC, UN News)*
- Anthropic's $81.3bn IPO is the biggest ever: priced at $83, shares open 34% higher on their Nasdaq debut, then pull back. *(Reuters, BusinessWorld)*
- Cyclone Akvan crosses the Odisha coast near Gopalpur; 300,000 people evacuated, 423 rescue teams deployed, 69 trains cancelled. *(The Hindu, IMD)*
- A Houthi strike damages the PIF Tower in Riyadh, home of the Saudi wealth fund; windows blown out over seven floors, no injuries. *(Reuters)*
- Trump says there is no rush on Iran: he will "see what happens" after 1 January, pushing any decision into 2027. *(Reuters, The Times of India)*
- Also today: NASA confirms Voyager 1 is one light-day from Earth, the first human-made object to reach it; European leaders say they are ready for talks with Russia on ending the Ukraine war.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library + PIL only, no network. Deterministic: two runs write the same bytes.

## License

MIT — see `LICENSE`.
