import shutil
import subprocess


def test_entry_point():
    proc = subprocess.run(
        [shutil.which("pylaia-htr-dataset-validate"), "-h"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    help = proc.stdout.decode()
    help = " ".join(help.split())
    assert help.startswith("usage: pylaia-htr-dataset-validate")
    assert (
        "Mapping from strings to integers. The CTC symbol must be mapped to integer 0 (required, type: str)"
        in help
    )
    assert (
        "Directories containing segmented line images (required, type: List[str])"
        in help
    )
    assert "Train labels (required, type: str)" in help
    assert "Val labels (required, type: str)" in help
    assert "Test labels (required, type: str)" in help


EXPECTED_CONFIG = """syms: null
img_dirs: []
tr_txt_table: null
va_txt_table: null
te_txt_table: null
fixed_input_height: 0
statistics_output: statistics.md
common:
  seed: 74565
  train_path: ''
  model_filename: model
  experiment_dirname: experiment
  monitor: va_cer
  checkpoint: null
train:
  delimiters:
  - <space>
  checkpoint_k: 3
  resume: false
  pretrain: false
  freeze_layers: []
  early_stopping_patience: 20
  gpu_stats: false
  augment_training: false
  log_to_wandb: false
logging:
  fmt: '[%(asctime)s %(levelname)s %(name)s] %(message)s'
  level: INFO
  filepath: null
  overwrite: false
  to_stderr_level: ERROR"""


def test_config_output():
    proc = subprocess.run(
        [shutil.which("pylaia-htr-dataset-validate"), "--print_config"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    config = proc.stdout.decode().strip()
    assert config == EXPECTED_CONFIG
