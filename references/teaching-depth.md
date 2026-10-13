# Detailed teaching standard

Use this when writing or reviewing substantive courseware pages. The target result resembles a patient one-to-one lesson, not an expanded list of slide bullets. If a learner provides a sample explanation, treat it as a **style and depth reference**, not an authority for subject facts or permission to copy its text, images, links, or errors. Verify claims against the actual courseware and sound reasoning.

## What a taught page should do

For each knowledge page, use the natural structure of the material rather than a mandatory template. Include the following when relevant:

1. **Locate and connect.** Give the page number or stable ID, name what the slide actually introduces, and explain why it follows the preceding page. If a later page continues a derivation, remind the learner of the exact established result needed here.
2. **Build prerequisites before using them.** Assume no course background by default. Define a term in ordinary language, then give its precise course meaning. For a symbol, explain its quantity, sign or direction, units, and whether it is a scalar, vector, or operation. Distinguish similar symbols used for different quantities.
3. **Explain the mechanism.** Turn each claim into a causal story: what changes, what causes it, what remains fixed, and what conclusion follows. For a diagram, describe the parts, arrows, labels, relative positions, and what the figure is meant to prove. Do not silently replace a visual argument with a formula.
4. **Derive rather than announce.** State the setup, assumptions, coordinate or normal direction, known equations, and the target. Write the intermediate expressions in order. At every non-obvious transition, say what operation was performed and why it is valid. Check signs, units, limiting cases, and physical meaning of the result. When a theorem is invoked, explain what its input and output represent; prove the theorem only if the course needs that proof.
5. **Make it concrete.** When helpful, use one small numerical or everyday example and show substitution and units. Contrast commonly confused cases, such as positive/negative, inside/outside, scalar/vector, uniform/nonuniform, or free/bound charge. State the scope of a simplified model.
6. **Close the loop.** End a concept or multi-page derivation with a short plain-language conclusion and, when useful, a small understanding check. This comes **after** the full explanation and cannot replace it.

For a sparse page, do not manufacture paragraphs to meet a word count. For a dense page, allow a long explanation. Aim for comparable **completeness relative to source density** across early and late pages. A later page containing new math should never become only “substitute into the formula and get the answer” when earlier derivations were unpacked.

## Multi-page derivations

Keep page-specific sections and source locators even when one proof spans several slides. At the first page, state the question and setup. On each following page, explicitly name the previous page's result, carry it forward, explain the new step, and say what remains to be shown. At the end, retrace the complete chain briefly so the learner can see why the final formula follows. Do not mark an intermediate page `taught` merely because a later page supplies the missing explanation without a clear cross-reference.

## Formula display for phone or tablet

Make the Markdown understandable in an ordinary viewer without math rendering by default, including on phones and tablets. Use plain text and Unicode symbols when legible, with short equations on separate lines and a sentence before or after each important step. Example:

```text
F⃗ = qE⃗
q = −e
F⃗ = −eE⃗
因此 F⃗ 的方向与 E⃗ 相反。
```

Define unfamiliar notation immediately. For lengthy expressions, use line breaks and consistent text subscripts such as `P_x` if Unicode subscripts would become ambiguous. Avoid raw `\frac`, `\nabla`, or other TeX commands as the only readable form. If the learner requests LaTeX or a particular display style, follow that preference; for advanced formulas, prioritize unambiguous notation and offer a plain-language reading. Do not turn equations into Markdown headings solely to make them look large.

## Source-to-explanation review

Before marking each page `taught`, compare its rendered slide and page inventory with the written section. A few short source-element labels in your working notes are enough; do not copy the whole slide into another checklist:

- Every meaningful definition, assertion, formula, derivation step, diagram, table, question, example, and exception is addressed or explicitly flagged unreadable.
- The explanation adds the missing “why/how” rather than only paraphrasing the slide.
- Every introduced symbol and sign convention is understandable to the learner at this point in the course.
- Claims, supplementary background, corrections, and invented practice examples are distinguishable.
- Cross-page references and the next page are accurate.

Repeat this check for late pages with the same care. For a longer batch, spot-check the last knowledge page and the most demanding formula, visual, or question page against the source. One page can satisfy both checks; skip the extra pass for a short batch just checked page by page. Expand the recheck only when it finds a concrete omission or shallow explanation. A character-count warning from `course_notes.py` is only a reason to review, not a substitute for this comparison. If a short page is genuinely complete, record the reason in the progress file.
