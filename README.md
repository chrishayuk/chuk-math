## TODO
- Use the LLM to produce a nice answer from question and result
- Integrate the explanation
- Use the LLM to smooth out the explanation
- Add the rest of the instructions
- Add a judge model for validating

## Install Dependencies
To install dependencies

```bash
pip install -r requirements.txt
```

## Unit Test
To run unit testing

```bash
pytest
```

## execute

```bash
python main.py "3 + 5 * (10 - 4)" --mode ast --llm "mistral-nemo"
```