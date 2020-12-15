# -*- coding: utf-8 -*-
"""Module with a class to generate wordclouds based on cleaned text"""

import logging
from typing import List, AnyStr
import pandas as pd
from io import BytesIO
from collections import Counter
import random
import os
import pathvalidate

import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from spacy_tokenizer import MultilingualTokenizer
from utils import time_logging
from font_exceptions_dict import FONT_EXCEPTIONS_DICT
from language_dict import SUPPORTED_LANGUAGES_SPACY

matplotlib.use("agg")


class PluginUnsupportedLanguageWarning(Warning):
    """Custom warning raised when an unsupported language is detected in a language column"""

    pass


class WordcloudVisualizer:
    """Class to generate multilingual wordclouds based on text data and save them as png images

    Attributes:
        df (pandas.DataFrame): Dataframe containing text data
        tokenizer (MultilingualTokenizer): Tokenizer used for text processing
        text_column (str): Name of the df column on which to compute wordclouds
        language (str, optional): Language in which to tokenize data (for monolingual wordcloud), defaults to english.
            Use "Detected language column" for multilingual tokenization
        language_column (str, optional): Name of the language column
        subchart_column (str, optional): Name of the subcharts column to compute wordclouds on, defaults to None
        max_words (int, optional): Maximum number of words to display in wordcloud, defaults to 100

    """

    DEFAULT_MAX_WORDS = 100
    DEFAULT_COLOR_LIST = [
        "hsl(205,71%,41%)",
        "hsl(214,56%,80%)",
        "hsl(28,100%,53%)",
        "hsl(30,100%,74%)",
        "hsl(120,57%,40%)",
        "hsl(110,57%,71%)",
    ]
    DEFAULT_FONT = "NotoSansDisplay-Regular.ttf"
    DEFAULT_SCALE = 6.8
    DEFAULT_MARGIN = 4
    DEFAULT_RANDOM_STATE = 3
    DEFAULT_FIGSIZE = (38.4, 21.6)
    DEFAULT_DPI = 100
    DEFAULT_TITLEPAD = 60
    DEFAULT_TITLESIZE = 60
    DEFAULT_PAD_INCHES = 1
    DEFAULT_BBOX_INCHES = "tight"

    def __init__(
        self,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        font_path: AnyStr,
        language: AnyStr = "en",
        language_column: AnyStr = None,
        subchart_column: AnyStr = None,
        max_words: int = DEFAULT_MAX_WORDS,
        color_list: List = DEFAULT_COLOR_LIST,
        font: str = DEFAULT_FONT,
        scale: float = DEFAULT_SCALE,
        margin: float = DEFAULT_MARGIN,
        random_state: int = DEFAULT_RANDOM_STATE,
        figsize: tuple = DEFAULT_FIGSIZE,
        dpi: int = DEFAULT_DPI,
        titlepad: int = DEFAULT_TITLEPAD,
        titlesize: int = DEFAULT_TITLESIZE,
        pad_inches: int = DEFAULT_PAD_INCHES,
        bbox_inches: str = DEFAULT_BBOX_INCHES,
    ):
        """Initialization method for the MultilingualTokenizer class, with optional arguments etailed above"""

        self.tokenizer = tokenizer
        self.text_column = text_column
        self.font_path = font_path
        self.language = language
        self.language_column = language_column
        self.subchart_column = subchart_column
        self.language_as_subchart = self.language_column == self.subchart_column
        self.max_words = max_words
        self.color_list = color_list
        self.font = font
        self.scale = scale
        self.margin = margin
        self.random_state = random_state
        self.figsize = figsize
        self.dpi = dpi
        self.titlepad = titlepad
        self.titlesize = titlesize
        self.pad_inches = pad_inches
        self.bbox_inches = bbox_inches
        if self.subchart_column == "order66":
            self.font = "DeathStar.otf"
            self.subchart_column = None

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
        """Return the color function used in the wordcloud"""
        return random.choice(self.color_list)

    def _retrieve_font(self, language):
        """Return the font to use for a given language"""
        return FONT_EXCEPTIONS_DICT.get(language, self.font)

    def _get_wordcloud(self, frequencies, font_path):
        """Return a wordcloud file"""
        wordcloud = (
            WordCloud(
                background_color="white",
                scale=self.scale,
                margin=self.margin,
                max_words=self.max_words,
                font_path=font_path,
            )
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=self.random_state)
        )

        return wordcloud

    def _generate_wordcloud(self, frequencies, title, language):
        """Return a wordcloud as a matplotlib figure"""
        # Manage font exceptions based on language
        font = self._retrieve_font(language)
        font_path = os.path.join(self.font_path, font)
        # Generate wordcloud
        wc = self._get_wordcloud(frequencies, font_path)
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        fig.tight_layout()
        plt.axis("off")
        plt.rcParams["axes.titlepad"] = self.titlepad
        plt.rcParams["axes.titlesize"] = self.titlesize
        plt.title(title)
        plt.imshow(wc, interpolation="bilinear")
        return fig

    @time_logging(log_message="Preparing data")
    def _prepare_data(self, df: pd.DataFrame):
        if self.subchart_column or self.language_column:
            # Group data per language and subchart for tokenization
            group_columns = [col for col in [self.language_column, self.subchart_column] if col]
            df.dropna(subset=group_columns, inplace=True)
            df_grouped = df.groupby(group_columns)
            # Filter unsupported languages contained in detected language column
            if self.language_as_subchart:
                temp = []
                unsupported_lang = []
                for group_name, group in df_grouped:
                    if group_name[0] in SUPPORTED_LANGUAGES_SPACY:
                        temp.append((group_name, group))
                    else:
                        unsupported_lang.append(group_name[0])
                df_grouped = temp
                if unsupported_lang:
                    logging.warn(
                        f"Found {len(unsupported_lang)} unsupported languages: {', '.join(unsupported_lang)}.\
                             No wordcloud will be generated for these languages"
                    )

        else:
            # Simply format data similarly
            df_grouped = [(self.language, df)]

        return df_grouped

    def _tokenize_texts(self, df_grouped: list):
        """Tokenize each group of observations in its correct language"""
        # Get language and subchart name for each group
        texts = []
        group_names = []
        for name, group in df_grouped:
            texts.append([group[self.text_column].str.cat(sep=" ")])
            group_names.append(name)

        # Get tokenization languages differently depending on language/subchart settings combinations
        if not self.language_column and not self.subchart_column:
            languages = [self.language]
        elif self.language_column and self.subchart_column:
            languages, subcharts = zip(*group_names)
            languages = list(languages)
            self.subcharts = list(subcharts)
        elif self.subchart_column:
            self.subcharts = group_names
            languages = [self.language] * len(self.subcharts)
        else:
            print("GROUP_NAMES: ", group_names)
            languages = group_names

        print("LANGUAGES: ", languages)

        # Tokenize
        docs = [self.tokenizer.tokenize_list(text, language)[0] for text, language in zip(texts, languages)]

        return docs

    @time_logging(log_message="Counting tokens")
    def _count_tokens(self, docs: list):
        """Count tokens in each group"""
        counters = []
        for doc in docs:
            counter = Counter()
            for token in doc:
                counter[(token.text)] += 1  # Equivalently, token.lemma_
            counters.append(counter)
        logging.info("Count successful, aggregating counters according to chart settings")

        if not self.subchart_column:
            # sum the values with same keys
            counts = Counter()
            for d in counters:
                counts.update(d)

            counts = dict(counts)
            return counts
        else:
            counts_df = pd.DataFrame(
                list(zip(self.subcharts, counters)),
                columns=["subchart", "count"],
            )
            counts_df = counts_df.groupby(by=["subchart"]).agg({"count": "sum"})
            # remove subcharts emptied by filter
            counts_df = counts_df.loc[counts_df["count"] != {}, :]
            return counts_df

    @time_logging(log_message="Generating wordclouds")
    def generate_wordclouds(self, counts):
        """Generate wordclouds and yield them as png images"""
        if self.subchart_column:
            for name, row in counts.iterrows():
                # Generate file name and chart title
                output_file_name = pathvalidate.sanitize_filename(
                    f"wordcloud_{self.subchart_column}_{name}.png"
                ).lower()
                wordcloud_title = output_file_name[:-4]
                # Generate chart
                if self.language_as_subchart:
                    fig = self._generate_wordcloud(row["count"], wordcloud_title, name)
                else:
                    fig = self._generate_wordcloud(row["count"], wordcloud_title, self.language)
                # Return chart
                temp = BytesIO()
                fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
                yield (temp, output_file_name)
                plt.close()
        else:
            # Generate chart
            fig = self._generate_wordcloud(counts, "wordcloud", self.language)
            # Return chart
            temp = BytesIO()
            fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
            yield (temp, "wordcloud.png")
            plt.close()

    def prepare_and_count(self, df: pd.DataFrame):
        df_prepared = self._prepare_data(df)
        docs = self._tokenize_texts(df_prepared)
        counts = self._count_tokens(docs)
        return counts
