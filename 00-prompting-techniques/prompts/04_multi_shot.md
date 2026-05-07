# 04 — Multi-shot Prompting

## What it means

Multi-shot prompting means giving the model several examples before asking it to perform the actual task.

## How it is different from few-shot

Few-shot and multi-shot are very closely related.

A simple way to understand it:
- Few-shot = a few examples
- Multi-shot = more examples for stronger pattern control

## When to use it

Use multi-shot when:
- the task has many possible variations
- labels may overlap
- consistency is very important
- the model needs stronger guidance

## Demo task

Tag customer support messages using multiple labeled examples.

## Key idea

More examples can improve consistency when the task is slightly tricky.