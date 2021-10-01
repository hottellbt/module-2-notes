# Algorithmic Bias and Fairness

Algorithms are created by people and trained on human data. As a result,
although the processes may be objective, the objectivity is compromised by
biased data.

We all have bias. It becomes an issue when it morphs into harmful
discrimination.

## 5 Types of biases to look out for

1. Data reflects existing biases
2. Unbalanced classes in training data
3. Data doesn't capture the right value
4. Data amplified by feedback loop
5. Malicious data attack or manipulation

## Correlated Features

Even if data such as race is not collected, bias can still be introduced due to
**correlated features**. This is when data is unintentionally correlated with
other data.

**Example:** ZIP Codes can be correlated to race due to segregation. Purchasing
patterns can be correlated to gender. Sexual orientation is also (apparently!)
correlated with certain characteristics of a social media profile photo.

## Unbalanced classes in training data

If an AI has a large set of training data for people of Group A, but not much
for Group B, then it will likely have faulty results when analyzing members of
Group B.

**Example:** Facial recognition software failing for nonwhite people

## Data doesn't capture the right value

Some things are impossible to quantify with a single number. This can result in
easily fooled AI systems that give ridiculous ratings based on simple criteria.

**Example:** Good writing is hard to define, and an AI to detect good writing
could be fooled by another AI.

## Data amplified by feedback loop

**Example:** PREDPOL would send police to areas with a relatively high amount of
racial minorities. More arrests occur due to a higher police presence, causing
PREDPOL to send even more police.

## Malicious data attack or manipulation

**Example:** Microsoft's chat AI "Tay" was trained by users to be sexist,
racist, anti-semitic, etc.

## Conclusion

Because AI can clearly be manipulated or make mistakes, the output of AI should
be taken with a grain of salt. An AI system may be very good at finding
correlations, but it doesn't understand correlation vs causation, and it can be
coerced or compromised into acting biased.
