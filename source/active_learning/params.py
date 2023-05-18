import argparse
import os
import yaml
from source.training.params import load_params

def parse_al_args(al_args):
  parser = argparse.ArgumentParser()
  
  # General
  parser.add_argument('--project-config-fp', type=str, required=True)
  parser.add_argument('--seed', type=int, default=0, help="random seed")
  parser.add_argument('--sample-duration', type = float, default = 30, help = 'duration of clip to sample for annotation, in seconds')
  parser.add_argument('--max-n-clips-to-sample', type = int, default = 120, help = 'how many clips to sample')
  parser.add_argument('--sampling-method', type=str, default='uncertainty', help = 'what method to use when sampling clips', choices = ['uncertainty', 'random', 'coreset'])
  parser.add_argument('--sampling-iteration', type=int, default=0, help = 'how many times have data previously been sampled and annotated for this project')
  parser.add_argument('--query-oracle', action='store_true', help="for benchmarking, will use predefined annotations to simulate active learning annotation step")
  parser.add_argument('--output-sr', type=int, default=16000, help="sr for output audio")
  
  # parser.add_argument('--model-checkpoint-fp', type=str, required=True, help = "filepath of model checkpoint")
  # parser.add_argument('--name', type=str, required=True)
  # parser.add_argument('--candidate-manifest-fp', required=True, help='fp to tsv list of wav files to sample')

  # Model based (Core set and Uncertainty) sampling
  parser.add_argument('--model-args-fp', type=str, help = "filepath of model params saved as a yaml")
  
  # Core Set based sampling
  ## Defaults if trained detection model is not used
  parser.add_argument('--sr', type=int, default=16000)
  parser.add_argument('--scale-factor', type=int, default = 320, help = "downscaling performed by aves")
  parser.add_argument('--aves-model-weight-fp', type=str, default = "/home/jupyter/carrion_crows/clip/pretrained_weights/aves-base-bio.pt")
  
  # Uncertainty based sampling  
  parser.add_argument('--uncertainty-clips-per-file', type = int, default = 1, help = 'maximum clips to sample per file')
  parser.add_argument('--uncertainty-discount-factor', type = float, default = 0.8, help = 'geometric weighting of uncertainties. Uncertainties are sorted and then the lower ranking uncertainties count for less. Closer to 0 discourages sampling clips with lots of detections')
  parser.add_argument('--uncertainty-detection-threshold', type=float, default = 0.1, help = 'ignore detection peaks lower than this value, for the purpose of computing uncertainty')
  
  # Random sampling
  parser.add_argument('--random-clips-per-file', type = int, help = 'maximum clips to sample per file')

  al_args = parser.parse_args(al_args)  
  return al_args

def expand_al_args(al_args):
  
  project_config = load_params(al_args.project_config_fp)
  setattr(al_args, "project_dir", project_config.project_dir)  
  
  output_dir = os.path.join(al_args.project_dir, "active_learning")
  setattr(al_args, 'output_dir', output_dir)
  if not os.path.exists(al_args.output_dir):
    os.makedirs(al_args.output_dir)
    
  if al_args.sampling_iteration > 0:
    prev_iter_fp = os.path.join(al_args.output_dir, f"train_info_iter_{al_args.sampling_iteration - 1}")
    assert os.path.exists(prev_iter_fp)
    setattr(al_args, 'prev_iteration_info_fp', prev_iter_fp)
  else:
    setattr(al_args, 'prev_iteration_info_fp', None)
    
  setattr(al_args, "name", f"iter_{al_args.sampling_iteration}")    
  
  
  return al_args

def save_al_params(al_args):
  """ Save a copy of the params used for this experiment """
  params_file = os.path.join(al_args.output_dir, f"{al_args.name}_params.yaml")

  args_dict = {}
  for name in sorted(vars(al_args)):
    val = getattr(al_args, name)
    args_dict[name] = val

  with open(params_file, "w") as f:
    yaml.dump(args_dict, f)