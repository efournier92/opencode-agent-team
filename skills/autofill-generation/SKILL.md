---
name: autofill-generation
description: Generate a randomized browser-autofill script for a given UI form so developers can populate an entire form in one devtools-snippet run instead of typing test data repeatedly.
license: MIT
compatibility: opencode
---

# autofill-generation

## Role

Generates a randomized browser-autofill script for a given UI form, so a developer can populate an entire form in one run (pasted into the browser devtools snippet runner) instead of manually typing test data repeatedly.

## Design

A reusable engine (shared script, not rewritten per form) already solves the hard browser problems: framework-controlled inputs, custom dropdown/select components, masked/formatted fields, default-checked options, and fields that only appear conditionally after another answer. **Per form, only two things ever change**: the wrapper function's name, and the value-selection function that maps each field to a plausible random value. The engine itself is never rewritten per form.

## Workflow

1. **Discover the form's fields**: read the form's entry component and follow what it renders — field names as registered with the form library, the validation schema (often a sibling file) for required-ness and enum constraints, generated types for enum/union options, labels/placeholders/masks for formatting hints, and conditionally-revealed sections (the engine's own retry loop fills these in once they appear — just make sure the value function has answers ready for them). Delegate broad reads to a subagent when the form spans many nested components; only field name/type/format/enum facts need to come back.
2. **Determine the output filename** using a convention that encodes which multi-step flow the form belongs to and its position in that flow — found by locating the flow's ordered step registry and finding this form's index in it. Ask the user rather than guessing if the flow/step position is ambiguous.
3. **Generate the script**: copy the engine template to the new file, rename the wrapper function to match the feature, and edit *only* the marked customization block — the value-selection function (matched by field name/id/placeholder/label, using discovered enum values and correct formats for dates/masked fields, with more specific matches ordered before broader ones) and the list of label substrings for any yes/no-style control that must always resolve to a specific answer (e.g. one that's required to be affirmative for the form to validate — checkbox-style consent controls are typically handled generically by the engine and need no per-form entry). Leave the rest of the engine untouched.
4. **Hand off**: tell the user to paste the file into their browser's devtools snippet runner and execute it there — never suggest console paste or a bookmarklet, both are unreliable for this kind of multi-step, event-driven form filling.

## Notes

- If the codebase has no frontend test suite, don't generate any test for the autofill script itself.
- A deprecation warning from the one browser API capable of real keystroke simulation for masked inputs is expected and acceptable output noise.
