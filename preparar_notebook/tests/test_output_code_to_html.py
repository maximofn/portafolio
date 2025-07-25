import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.jupyter_notebook_to_html.jupyter_notebook_to_html import output_code_to_html

class TestOutputCodeToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one_line(self):
        output_code = "Detected language: en"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>Detected language: en
</pre>
</div>
</div>
</div>
</section>'''
        self.assertEqual(output_code_to_html(output_code), expected_html)
    
    def test_one_line_with_endline_at_the_end(self):
        output_code = "Detected language: en\n"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>Detected language: en
</pre>
</div>
</div>
</div>
</section>'''
        self.assertEqual(output_code_to_html(output_code), expected_html)
    
    def test_micromachines_output(self):
        output_code = '"This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There\'s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you\'ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are."'
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt-output-prompt">Out[]:</div>
<div class="output-text-output-subareaoutput_execute_result">
<pre>&quot;This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There&#x27;s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you&#x27;ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are.&quot;</pre>
</div>
</div>
</div>
</section>'''
        self.assertEqual(output_code_to_html(output_code), expected_html)
    
    def test_output_code_with_multiple_lines_and_indentation(self):
        output_code = "[{'score': 0.05116177722811699,\n  'token': 8422,\n  'token_str': 'stanford',\n  'sequence': 'i am a student at stanford university.'},\n {'score': 0.04033993184566498,\n  'token': 5765,\n  'token_str': 'harvard',\n  'sequence': 'i am a student at harvard university.'},\n {'score': 0.03990468755364418,\n  'token': 7996,\n  'token_str': 'yale',\n  'sequence': 'i am a student at yale university.'},\n {'score': 0.0361952930688858,\n  'token': 10921,\n  'token_str': 'cornell',\n  'sequence': 'i am a student at cornell university.'},\n {'score': 0.03303057327866554,\n  'token': 9173,\n  'token_str': 'princeton',\n  'sequence': 'i am a student at princeton university.'}]"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>[&#x7B;&#x27;score&#x27;: 0.05116177722811699,
&#x20;&#x20;&#x27;token&#x27;: 8422,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;stanford&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at stanford university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.04033993184566498,
&#x20;&#x20;&#x27;token&#x27;: 5765,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;harvard&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at harvard university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.03990468755364418,
&#x20;&#x20;&#x27;token&#x27;: 7996,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;yale&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at yale university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.0361952930688858,
&#x20;&#x20;&#x27;token&#x27;: 10921,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;cornell&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at cornell university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.03303057327866554,
&#x20;&#x20;&#x27;token&#x27;: 9173,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;princeton&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at princeton university.&#x27;&#x7D;]
</pre>
</div>
</div>
</div>
</section>'''
        html_output = output_code_to_html(output_code)
        self.assertEqual(html_output, expected_html)

    def test_output_code_with_ansi_escape_code(self):
        output_code = "Cloning into 'LLMs-from-scratch'...\nremote: Enumerating objects: 260, done.\x1b[K\nremote: Counting objects: 100% (260/260), done.\x1b[K\nremote: Compressing objects: 100% (226/226), done.\x1b[K\nremote: Total 260 (delta 61), reused 121 (delta 22), pack-reused 0 (from 0)\x1b[K\nReceiving objects: 100% (260/260), 1.64 MiB | 6.94 MiB/s, done.\nResolving deltas: 100% (61/61), done.\n"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>Cloning into &#x27;LLMs-from-scratch&#x27;...
remote: Enumerating objects: 260, done.
remote: Counting objects: 100% (260/260), done.
remote: Compressing objects: 100% (226/226), done.
remote: Total 260 (delta 61), reused 121 (delta 22), pack-reused 0 (from 0)
Receiving objects: 100% (260/260), 1.64 MiB | 6.94 MiB/s, done.
Resolving deltas: 100% (61/61), done.
</pre>
</div>
</div>
</div>
</section>'''
        html_output = output_code_to_html(output_code)
        self.assertEqual(html_output, expected_html)
    
    def test_output_code_with_backslash(self):
        output_code = '---------------------------------------------------------------------------ValueError                                Traceback (most recent call last)Cell In[21], line 1\n----&gt; 1 trainer.train()\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/trainer.py:1876, in Trainer.train(self, resume_from_checkpoint, trial, ignore_keys_for_eval, **kwargs)\n   1873 try:\n   1874     # Disable progress bars when uploading models during checkpoints to avoid polluting stdout\n   1875     hf_hub_utils.disable_progress_bars()\n-&gt; 1876     return inner_training_loop(\n   1877         args=args,\n   1878         resume_from_checkpoint=resume_from_checkpoint,\n   1879         trial=trial,\n   1880         ignore_keys_for_eval=ignore_keys_for_eval,\n   1881     )\n   1882 finally:\n   1883     hf_hub_utils.enable_progress_bars()\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/trainer.py:2178, in Trainer._inner_training_loop(self, batch_size, args, resume_from_checkpoint, trial, ignore_keys_for_eval)\n   2175     rng_to_sync = True\n   2177 step = -1\n-&gt; 2178 for step, inputs in enumerate(epoch_iterator):\n   2179     total_batched_samples += 1\n   2181     if self.args.include_num_input_tokens_seen:\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/accelerate/data_loader.py:454, in DataLoaderShard.__iter__(self)\n    452 # We iterate one batch ahead to check when we are at the end\n    453 try:\n--&gt; 454     current_batch = next(dataloader_iter)\n    455 except StopIteration:\n    456     yield\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/dataloader.py:631, in _BaseDataLoaderIter.__next__(self)\n    628 if self._sampler_iter is None:\n    629     # TODO(https://github.com/pytorch/pytorch/issues/76750)\n    630     self._reset()  # type: ignore[call-arg]\n--&gt; 631 data = self._next_data()\n    632 self._num_yielded += 1\n    633 if self._dataset_kind == _DatasetKind.Iterable and \\\n    634         self._IterableDataset_len_called is not None and \\\n    635         self._num_yielded &gt; self._IterableDataset_len_called:\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/dataloader.py:675, in _SingleProcessDataLoaderIter._next_data(self)\n    673 def _next_data(self):\n    674     index = self._next_index()  # may raise StopIteration\n--&gt; 675     data = self._dataset_fetcher.fetch(index)  # may raise StopIteration\n    676     if self._pin_memory:\n    677         data = _utils.pin_memory.pin_memory(data, self._pin_memory_device)\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/_utils/fetch.py:54, in _MapDatasetFetcher.fetch(self, possibly_batched_index)\n     52 else:\n     53     data = self.dataset[possibly_batched_index]\n---&gt; 54 return self.collate_fn(data)\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/data/data_collator.py:271, in DataCollatorWithPadding.__call__(self, features)\n    270 def __call__(self, features: List[Dict[str, Any]]) -&gt; Dict[str, Any]:\n--&gt; 271     batch = pad_without_fast_tokenizer_warning(\n    272         self.tokenizer,\n    273         features,\n    274         padding=self.padding,\n    275         max_length=self.max_length,\n    276         pad_to_multiple_of=self.pad_to_multiple_of,\n    277         return_tensors=self.return_tensors,\n    278     )\n    279     if "label" in batch:\n    280         batch["labels"] = batch["label"]\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/data/data_collator.py:66, in pad_without_fast_tokenizer_warning(tokenizer, *pad_args, **pad_kwargs)\n     63 tokenizer.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = True\n     65 try:\n---&gt; 66     padded = tokenizer.pad(*pad_args, **pad_kwargs)\n     67 finally:\n     68     # Restore the state of the warning.\n     69     tokenizer.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = warning_state\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/tokenization_utils_base.py:3299, in PreTrainedTokenizerBase.pad(self, encoded_inputs, padding, max_length, pad_to_multiple_of, return_attention_mask, return_tensors, verbose)\n   3297 # The model\'s main input name, usually `input_ids`, has be passed for padding\n   3298 if self.model_input_names[0] not in encoded_inputs:\n-&gt; 3299     raise ValueError(\n   3300         "You should supply an encoding or a list of encodings to this method "\n   3301         f"that includes {self.model_input_names[0]}, but you provided {list(encoded_inputs.keys())}"\n   3302     )\n   3304 required_input = encoded_inputs[self.model_input_names[0]]\n   3306 if required_input is None or (isinstance(required_input, Sized) and len(required_input) == 0):\nValueError: You should supply an encoding or a list of encodings to this method that includes input_ids, but you provided [\'label\', \'labels\']'
        expectes_html = '''<section class="section-block-code-cell-">\n<div class="output-wrapper">\n<div class="output-area">\n<div class="prompt"></div>\n<div class="output-subarea-output-stream-output-stdout-output-text">\n<pre>---------------------------------------------------------------------------ValueError                                Traceback (most recent call last)Cell In[21], line 1\n----&amp;gt; 1 trainer.train()\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/trainer.py:1876, in Trainer.train(self, resume_from_checkpoint, trial, ignore_keys_for_eval, **kwargs)\n&#x20;&#x20;&#x20;1873 try:\n&#x20;&#x20;&#x20;1874     # Disable progress bars when uploading models during checkpoints to avoid polluting stdout\n&#x20;&#x20;&#x20;1875     hf_hub_utils.disable_progress_bars()\n-&amp;gt; 1876     return inner_training_loop(\n&#x20;&#x20;&#x20;1877         args=args,\n&#x20;&#x20;&#x20;1878         resume_from_checkpoint=resume_from_checkpoint,\n&#x20;&#x20;&#x20;1879         trial=trial,\n&#x20;&#x20;&#x20;1880         ignore_keys_for_eval=ignore_keys_for_eval,\n&#x20;&#x20;&#x20;1881     )\n&#x20;&#x20;&#x20;1882 finally:\n&#x20;&#x20;&#x20;1883     hf_hub_utils.enable_progress_bars()\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/trainer.py:2178, in Trainer._inner_training_loop(self, batch_size, args, resume_from_checkpoint, trial, ignore_keys_for_eval)\n&#x20;&#x20;&#x20;2175     rng_to_sync = True\n&#x20;&#x20;&#x20;2177 step = -1\n-&amp;gt; 2178 for step, inputs in enumerate(epoch_iterator):\n&#x20;&#x20;&#x20;2179     total_batched_samples += 1\n&#x20;&#x20;&#x20;2181     if self.args.include_num_input_tokens_seen:\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/accelerate/data_loader.py:454, in DataLoaderShard.__iter__(self)\n&#x20;&#x20;&#x20;&#x20;452 # We iterate one batch ahead to check when we are at the end\n&#x20;&#x20;&#x20;&#x20;453 try:\n--&amp;gt; 454     current_batch = next(dataloader_iter)\n&#x20;&#x20;&#x20;&#x20;455 except StopIteration:\n&#x20;&#x20;&#x20;&#x20;456     yield\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/dataloader.py:631, in _BaseDataLoaderIter.__next__(self)\n&#x20;&#x20;&#x20;&#x20;628 if self._sampler_iter is None:\n&#x20;&#x20;&#x20;&#x20;629     # TODO(https://github.com/pytorch/pytorch/issues/76750)\n&#x20;&#x20;&#x20;&#x20;630     self._reset()  # type: ignore[call-arg]\n--&amp;gt; 631 data = self._next_data()\n&#x20;&#x20;&#x20;&#x20;632 self._num_yielded += 1\n&#x20;&#x20;&#x20;&#x20;633 if self._dataset_kind == _DatasetKind.Iterable and \\\\\n&#x20;&#x20;&#x20;&#x20;634         self._IterableDataset_len_called is not None and \\\\\n&#x20;&#x20;&#x20;&#x20;635         self._num_yielded &amp;gt; self._IterableDataset_len_called:\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/dataloader.py:675, in _SingleProcessDataLoaderIter._next_data(self)\n&#x20;&#x20;&#x20;&#x20;673 def _next_data(self):\n&#x20;&#x20;&#x20;&#x20;674     index = self._next_index()  # may raise StopIteration\n--&amp;gt; 675     data = self._dataset_fetcher.fetch(index)  # may raise StopIteration\n&#x20;&#x20;&#x20;&#x20;676     if self._pin_memory:\n&#x20;&#x20;&#x20;&#x20;677         data = _utils.pin_memory.pin_memory(data, self._pin_memory_device)\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/torch/utils/data/_utils/fetch.py:54, in _MapDatasetFetcher.fetch(self, possibly_batched_index)\n&#x20;&#x20;&#x20;&#x20;&#x20;52 else:\n&#x20;&#x20;&#x20;&#x20;&#x20;53     data = self.dataset[possibly_batched_index]\n---&amp;gt; 54 return self.collate_fn(data)\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/data/data_collator.py:271, in DataCollatorWithPadding.__call__(self, features)\n&#x20;&#x20;&#x20;&#x20;270 def __call__(self, features: List[Dict[str, Any]]) -&amp;gt; Dict[str, Any]:\n--&amp;gt; 271     batch = pad_without_fast_tokenizer_warning(\n&#x20;&#x20;&#x20;&#x20;272         self.tokenizer,\n&#x20;&#x20;&#x20;&#x20;273         features,\n&#x20;&#x20;&#x20;&#x20;274         padding=self.padding,\n&#x20;&#x20;&#x20;&#x20;275         max_length=self.max_length,\n&#x20;&#x20;&#x20;&#x20;276         pad_to_multiple_of=self.pad_to_multiple_of,\n&#x20;&#x20;&#x20;&#x20;277         return_tensors=self.return_tensors,\n&#x20;&#x20;&#x20;&#x20;278     )\n&#x20;&#x20;&#x20;&#x20;279     if &quot;label&quot; in batch:\n&#x20;&#x20;&#x20;&#x20;280         batch[&quot;labels&quot;] = batch[&quot;label&quot;]\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/data/data_collator.py:66, in pad_without_fast_tokenizer_warning(tokenizer, *pad_args, **pad_kwargs)\n&#x20;&#x20;&#x20;&#x20;&#x20;63 tokenizer.deprecation_warnings[&quot;Asking-to-pad-a-fast-tokenizer&quot;] = True\n&#x20;&#x20;&#x20;&#x20;&#x20;65 try:\n---&amp;gt; 66     padded = tokenizer.pad(*pad_args, **pad_kwargs)\n&#x20;&#x20;&#x20;&#x20;&#x20;67 finally:\n&#x20;&#x20;&#x20;&#x20;&#x20;68     # Restore the state of the warning.\n&#x20;&#x20;&#x20;&#x20;&#x20;69     tokenizer.deprecation_warnings[&quot;Asking-to-pad-a-fast-tokenizer&quot;] = warning_state\nFile ~/miniconda3/envs/nlp_/lib/python3.11/site-packages/transformers/tokenization_utils_base.py:3299, in PreTrainedTokenizerBase.pad(self, encoded_inputs, padding, max_length, pad_to_multiple_of, return_attention_mask, return_tensors, verbose)\n&#x20;&#x20;&#x20;3297 # The model&#x27;s main input name, usually `input_ids`, has be passed for padding\n&#x20;&#x20;&#x20;3298 if self.model_input_names[0] not in encoded_inputs:\n-&amp;gt; 3299     raise ValueError(\n&#x20;&#x20;&#x20;3300         &quot;You should supply an encoding or a list of encodings to this method &quot;\n&#x20;&#x20;&#x20;3301         f&quot;that includes &#x7B;self.model_input_names[0]&#x7D;, but you provided &#x7B;list(encoded_inputs.keys())&#x7D;&quot;\n&#x20;&#x20;&#x20;3302     )\n&#x20;&#x20;&#x20;3304 required_input = encoded_inputs[self.model_input_names[0]]\n&#x20;&#x20;&#x20;3306 if required_input is None or (isinstance(required_input, Sized) and len(required_input) == 0):\nValueError: You should supply an encoding or a list of encodings to this method that includes input_ids, but you provided [&#x27;label&#x27;, &#x27;labels&#x27;]\n</pre>\n</div>\n</div>\n</div>\n</section>'''
        html_output = output_code_to_html(output_code)
        self.assertEqual(html_output, expectes_html)


if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
