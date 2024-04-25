# BGHinsights - Automatically analyze BGH Judgements

This is a data processing library to extract the text from BGH-Judgement pdf's and analyze it's content. Common use cases for this library are large scale qunatitative judgement analysis and judgement discorvery. Together with a search engine you can use this library as a simple ETL-Software as well. See an example of a search tool that we built on top of the extracted data [here](https://github.com/progius/bgh-search).
## Usage
First set the environment variables in the `.env.sample` file, if you want to use an Azure Storage to handle all of the judgement data and rename it to `.env`.
Afterwards you can simply use poetry to install the library and it's dependencies:

```sh
poetry install
```

Feel free to fork and adapt this library for your own needs 😄.