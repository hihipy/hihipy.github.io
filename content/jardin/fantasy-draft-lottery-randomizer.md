---
title: "fantasy-draft-lottery-randomizer"
weight: 30
description: "A Python GUI that runs fantasy sports draft lotteries with three distribution modes, a dramatic reverse reveal, and an audit-trail output that embeds its own source code so league members can verify the result."
summary: "Auditable fantasy draft lottery."
tags: ["python", "tkinter", "asyncio", "combinatorics", "side-project"]
showDate: false
showReadingTime: false
showAuthor: false
---

{{< katex >}}

{{< lead >}}
A draft-pick randomizer for fantasy sports leagues, designed so league members can verify the result was actually fair.
{{< /lead >}}

## At a Glance

Fantasy sports leagues have a problem that real sports leagues solved decades ago: how do you assign draft order in a way that everyone agrees is fair? Real leagues use weighted lotteries with physical ping-pong balls, televised live, with a transparent process every team can verify. Fantasy leagues usually default to "the commissioner's spreadsheet did it" and then argue afterward.

This tool runs the lottery. It supports three distribution modes (straight random, weighted, or fully custom), shows the results with a dramatic reveal animation, and saves a results file that includes the final order, the math behind the odds, and the entire Python source code that produced the result. League members can audit the run themselves, or feed the source into an AI assistant to do it for them.

## The Problem

The argument about fantasy lottery fairness is not really about fairness. It is about verifiability. Every commissioner says their spreadsheet is fair. Most of them are telling the truth. None of them can prove it after the fact.

Three failure modes show up in practice.

**The opaque draw.** The commissioner runs a tool, announces the order, and that is it. There is no record of the random seed, the distribution used, or the math that produced the result. If anyone disputes the order later, there is nothing to point to.

**The unwitnessed draw.** The commissioner runs the lottery in private and reports the outcome. Even if the tool is fair and the commissioner is honest, the absence of a witness or a record means there is no defense against accusations.

**The unverifiable math.** Most lottery tools that do exist hide their logic. A user sees an order pop out but cannot tell whether the weighting actually produced the right odds, whether ties were broken consistently, or whether the same seed would produce the same result twice.

This tool addresses all three by writing a complete results file at the end of every lottery: the order, the math, the timestamp, the version of the script, and the script itself.

## The Approach

A Tkinter desktop app that runs entirely locally. Three core flows:

1. **League management.** Create leagues, add managers, configure ball counts. Multiple leagues can be saved and reused across seasons.
2. **Distribution setup.** Pick one of three modes per league. Straight gives every manager equal weight. Weighted lets the user enter a ball count per manager (typically based on prior-season standings, with worse records getting more balls). Custom is a manual override for any other arrangement.
3. **The lottery itself.** A virtual ball pool is built from the distribution, balls are drawn one at a time, the picked manager is removed from the pool, and the process repeats until every position is filled.

The reveal animation runs in reverse. The last pick is shown first, and each earlier pick is revealed with a delay, building toward the first-overall pick at the end. This mirrors how real sports lotteries (the NBA's most notably) reveal their results: the suspense is in the unrevealed positions, not the last one.

## The Math

### Simple Odds

For a manager with \\(b_i\\) balls out of \\(T\\) total balls, the probability of getting the first overall pick is straightforward:

$$P(\text{first pick}) = \frac{b_i}{T}$$

If a manager has 100 balls in a pool of 1,000, they have a 10% chance of going first. This is the number that gets quoted in lottery odds tables and is what most people mean when they say "the odds."

### Combinatorial Odds

The harder question is the probability of going at *exactly* position \\(k\\), for some \\(k\\) other than first. A manager with 10% of the balls does not have a 10% chance of going second, or third, or fourth. The probability depends on what happened at every earlier pick.

The probability of manager \\(i\\) going at position \\(k\\) is the probability that some other manager goes at every position from 1 through \\(k-1\\), and then manager \\(i\\) goes at position \\(k\\). This requires summing over every possible sequence of earlier picks:

$$P(\text{position } k) = \sum_{\substack{j_1, j_2, \ldots, j_{k-1} \\ j_m \neq i}} \prod_{m=1}^{k-1} \frac{b_{j_m}}{T - \sum_{l < m} b_{j_l}} \cdot \frac{b_i}{T - \sum_{l < k} b_{j_l}}$$

The summation runs over every possible sequence of \\(k-1\\) earlier picks that does not include manager \\(i\\). The product computes the conditional probability of that exact sequence happening, with the denominator shrinking each round because picked managers are removed from the pool.

Written out for a small case (six teams, computing position 3 odds for one team), this sum has dozens of terms. The implementation does not enumerate them directly. It computes the result iteratively by tracking the "expected remaining ball mass" for each manager after each prior pick:

```python
@staticmethod
def exact_pick_odds(manager_balls, total_balls, pick_position):
    """Calculate the exact probability for each pick position using combinatorics."""
    remaining_balls = total_balls
    pick_probabilities = []

    for i in range(pick_position):
        pick_probabilities.append([balls / remaining_balls for balls in manager_balls])
        if i < pick_position - 1:
            # Adjust each manager's effective ball count for the next pick,
            # weighted by the probability they were not picked this round
            for j in range(len(manager_balls)):
                manager_balls[j] *= (remaining_balls - manager_balls[j]) / remaining_balls
            remaining_balls -= 1

    return pick_probabilities[-1]
```

The intuition: instead of enumerating all the ways a manager could have *not* been picked yet, the algorithm treats each manager's ball count as a random variable that decays by the probability they were picked at each previous round. After \\(k-1\\) rounds of decay, the remaining ball mass divided by the remaining total is the marginal probability of being picked at round \\(k\\).

The two odds (simple and combinatorial) are reported separately in the results file. For pick 1, they are identical. For later picks they diverge, sometimes substantially. A manager with a very large ball count will see their probability mass concentrate in the early picks; a manager with a very small ball count will see their probability spread more evenly across all positions.

## Why The Self-Embedding Source Matters

Every saved results file ends with a code block containing the complete Python source of the script that produced it. Verbatim. No summary, no version number, no diff against some reference version: the entire program.

This is unusual but deliberate. Three reasons.

**Reproducibility.** A league member who wants to verify the lottery can copy the embedded source into a fresh Python file, run it, and confirm that the same configuration produces a similar distribution of outcomes. They cannot reproduce the *exact* result without the random seed (which is not captured), but they can verify that the methodology matches what the commissioner ran.

**Auditing through AI.** Modern league members increasingly know how to feed code into ChatGPT or Claude and ask for an explanation. The embedded source makes this trivial: copy the code block, paste it into an LLM, ask "is this lottery actually fair?" The LLM does the math review the user could not do themselves.

**Tamper resistance.** If the commissioner modifies the script between runs, the embedded source in each saved file shows that. A side-by-side diff of two results files exposes any mid-season changes to the lottery logic. The source becomes part of the record.

The README of the project itself encourages this audit explicitly: *"Feel free to audit the code by either reviewing it yourself or feeding it into generative AI for auditing."* The transparency is not a side effect of the design; it is the design.

## Under The Hood

For the technically curious, three of the more interesting implementation pieces.

{{< accordion mode="collapse" separated="true" >}}

{{< accordionItem title="Building the ball pool from a distribution" >}}

The lottery draw treats the ball pool as a flat list of manager names, with each manager's name appearing in the list once for each ball they were assigned:

```python
# Use the correct balls and order from the chosen distribution
self.original_balls = dist_data.get('balls', [1] * len(self.league['managers']))
order = dist_data.get('order', self.league['managers'])

# Build the pool based on the distribution type
pool = []
for manager, ball_count in zip(order, self.original_balls):
    pool.extend([manager] * ball_count)

while len(self.selected_order) < len(self.league['managers']):
    pick = random.choice(pool)
    self.selected_order.append(pick)
    pool = [p for p in pool if p != pick]  # Remove selected manager from pool
```

Building the pool as a flat list of duplicated names means `random.choice(pool)` is implicitly weighted by ball count: a manager with 100 balls appears 100 times, so they are 100 times more likely to be picked than a manager with one ball. This is the simplest possible implementation of weighted random selection, and it has the useful property of being easy to verify by hand: a league member who wants to see what the pool actually looks like can print it.

After each pick, the chosen manager is removed entirely from the pool with a list comprehension. They cannot be picked twice, and their remaining balls (the ones that were not drawn) effectively get redistributed to the other managers proportionally.

The defaults at the top of the function (`[1] * len(managers)` and the manager list as the order) mean that even a misconfigured league still runs: every manager gets one ball, the pool is uniform, and the lottery degrades to plain random selection. It does not crash, it does not warn, it just runs. This is intentional. A commissioner setting up a new league should not have to configure a distribution before the tool can be tested.

{{< /accordionItem >}}

{{< accordionItem title="Reverse async reveal with skip-to-end" >}}

The dramatic reveal happens in `asyncio` because Tkinter does not handle long-running animations well by default: a synchronous `time.sleep()` loop blocks the GUI thread, freezing the entire window. The async approach lets the UI stay responsive while the animation runs.

```python
async def reveal_draft_order(self, selected_order):
    self.labels = []
    num_picks = len(selected_order)

    # Pre-create all label widgets with hidden text
    for idx, manager in enumerate(selected_order):
        label_text = f"{idx + 1}. ???"
        label = ttk.Label(self.result_frame, text=label_text)
        label.pack(anchor="w", pady=2)
        self.labels.append((label, f"{idx + 1}. {manager}"))

    # Reveal in REVERSE: last pick first, building tension toward 1st overall
    for idx, (label, text) in enumerate(reversed(self.labels)):
        if self.skip_reveal:
            break

        if label.winfo_exists():
            label.config(text=text)
            self.result_frame.update()
            await asyncio.sleep(REVEAL_DELAY)
```

Two design choices worth noting.

The labels are created up front with placeholder text (`1. ???`, `2. ???`, etc.) so the user sees the full list of pick positions before any reveal happens. This sets expectations: the user knows there will be ten picks, they know the order they will be revealed in, and they can count down with the animation.

The `reversed()` iterator means the last pick is updated first. From the user's perspective, the visible behavior is that the bottom of the list fills in first and the suspense is at the top: who gets first overall? The choice mirrors NBA Draft Lottery conventions, where the lottery presenter announces the seventh-to-fourth picks first, then the top three in reverse order.

The `skip_reveal` flag is checked inside the loop, not just at the start. This means a user who clicks Skip mid-reveal gets the rest of the picks immediately, not after waiting for the next iteration. The same flag triggers a "fill in everything" loop after the break, which catches up any labels that had not yet been revealed when the user skipped.

{{< /accordionItem >}}

{{< accordionItem title="Self-embedding source for the audit trail" >}}

The save routine writes the lottery result, then the odds explanation, then the league metadata, then the entire script source. The source-embedding step is a single block at the end:

```python
# Include the full Python script for auditing
f.write("=" * 80 + "\n")
f.write(f"{'FULL PYTHON SCRIPT':^80}\n")
f.write("=" * 80 + "\n")
f.write("```python\n")  # Start the code block
with open(__file__, 'r') as script_file:
    f.write(script_file.read())
f.write("\n```\n")  # End the code block
```

`__file__` is Python's built-in reference to the path of the currently-running script. Reading it with `open(__file__, 'r')` opens the script's own source for reading; the entire file gets copied verbatim into the results file. The Markdown code fences (` ```python `) wrap the source so the resulting file renders correctly when opened in any tool that understands Markdown (GitHub, Obsidian, VS Code, even Discord).

Two consequences worth noting.

The embedded source is the version that ran, not the latest version of the script. If a league has been running lotteries for three seasons and the commissioner has updated the script between seasons, each season's results file contains the version that produced that season's result. A side-by-side comparison of two results files surfaces any changes the commissioner made.

The size cost is small. The script is roughly a thousand lines, which adds about 30-40 KB to each results file. For a tool that is used a few times a season, this is trivial. The trade gets us complete reproducibility metadata for the cost of one large attachment per run.

The pattern is borrowed loosely from compliance-grade tooling: archive the analysis alongside the data. In domains like clinical trials and financial reporting, the embedded-script convention is standard. Bringing it to a fantasy sports tool is the kind of thing that does not strictly need to be done, but doing it costs almost nothing and forecloses an entire category of dispute.

{{< /accordionItem >}}

{{< /accordion >}}

## Stack

- **Language:** Python 3.7+
- **GUI:** tkinter (built into Python)
- **Concurrency:** `asyncio` for non-blocking reveal animation, `threading` for the asyncio event loop
- **Output formatting:** [tabulate](https://pypi.org/project/tabulate/) for grid-aligned results tables
- **Persistence:** plain JSON files in a known directory, no database

## Repo

[github.com/hihipy/fantasy-draft-lottery-randomizer](https://github.com/hihipy/fantasy-draft-lottery-randomizer)
