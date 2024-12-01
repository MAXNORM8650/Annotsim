import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import torch
import torchvision.utils


def gridify_output(img, row_size=-1):
    scale_img = lambda img: ((img + 1) * 127.5).clamp(0, 255).to(torch.uint8)
    return torchvision.utils.make_grid(scale_img(img), nrow=row_size, pad_value=-1).cpu().data.permute(
            0, 2,
            1
            ).contiguous().permute(
            2, 1, 0
            )
def gridify_output_with_annotations(img, row_size=-1, names = None, output_name = "res"):
    scale_img = lambda img: ((img + 1) * 127.5).clamp(0, 255).to(torch.uint8)
    grid = torchvision.utils.make_grid(scale_img(img), nrow=row_size, pad_value=-1).cpu().data.permute(0, 2, 1).contiguous().permute(2, 1, 0)

    # Calculate the number of rows needed for the grid
    num_images = img.shape[0]
    if row_size == -1:
        row_size = num_images
    num_rows = (num_images - 1) // row_size + 1

    # Determine the size of each image in the grid
    grid_height, grid_width, _ = grid.shape
    image_height = grid_height // num_rows
    image_width = grid_width // row_size

    # Create the plot and add the grid of images
    plt.figure(figsize=(row_size * 3, num_rows * 3))
    plt.imshow(grid, cmap = 'gray')

    # Add the name as text in the top-left corner of each image
    for i in range(num_images):
        row_idx = i // row_size
        col_idx = i % row_size
        if names is not None:
            image_name = names[i]
        else:
            image_name = f"Image {i+1}"
        text_x = (col_idx * image_width) + (image_width * 0.02)  # Adjust the 0.02 value to change the horizontal spacing of the text
        text_y = (row_idx * image_height) + (image_height * 0.02)  # Adjust the 0.02 value to change the vertical spacing of the text
        plt.text(text_x, text_y, image_name, fontsize=12, ha='left', va='top', color='white')
 
    plt.axis('off')
    plt.savefig(output_name + ".png")
    plt.close('all')


def defaultdict_from_json(jsonDict):
    func = lambda: defaultdict(str)
    dd = func()
    dd.update(jsonDict)
    return dd


def load_checkpoint(param, use_checkpoint, device):
    """
    loads the most recent (non-corrupted) checkpoint or the final model
    :param param: args number
    :param use_checkpoint: checkpointed or final model
    :return:
    """
    if not use_checkpoint:
        return torch.load(f'./model/diff-params-ARGS={param}/params-final.pt', map_location=device)
    else:
        checkpoints = os.listdir(f'./model/diff-params-ARGS={param}/checkpoint')
        checkpoints.sort(reverse=True)
        for i in checkpoints:
            try:
                file_dir = f"./model/diff-params-ARGS={param}/checkpoint/{i}"
                loaded_model = torch.load(file_dir, map_location=device)
                break
            except RuntimeError:
                continue
        return loaded_model


def load_parameters(device, argN = None):
    """
    Loads the trained parameters for the detection model
    :return:
    """
    import sys
    if argN is not None:
        print(f"Loading from {argN} Number")
#         params = os.listdir("./model")
        # Use a list comprehension to find the matching string
        params = [f'{argN}'] # [s for s in params if f'={argN}' in s]

    elif len(sys.argv[1:]) > 0:
        params = sys.argv[1:]
    else:
        params = os.listdir("./model")
    if ".DS_Store" in params:
        params.remove(".DS_Store")

    if params[0] == "CHECKPOINT":
        use_checkpoint = True
        params = params[1:]
    else:
        use_checkpoint = False
#     use_checkpoint = True
#     print(params)
    for param in params:
        if param.isnumeric():
            output = load_checkpoint(param, use_checkpoint, device)
        elif param[:4] == "args" and param[-5:] == ".json":
            output = load_checkpoint(param[4:-5], use_checkpoint, device)
        elif param[:4] == "args":
            output = load_checkpoint(param[4:], use_checkpoint, device)
        elif  isinstance(param, str):
            output = load_checkpoint(param, use_checkpoint, device)
        else:
            raise ValueError(f"Unsupported input {param}")

        if "args" in output:
            args = output["args"]
        else:
            try:
                with open(f'./test_args/args{param[17:]}.json', 'r') as f:
                    args = json.load(f)
                args['arg_num'] = param[17:]
                args = defaultdict_from_json(args)
            except FileNotFoundError:
                raise ValueError(f"args{param[17:]} doesn't exist for {param}")

        if "noise_fn" not in args:
            args["noise_fn"] = "gauss"

        return args, output


def main():
    pass


if __name__ == '__main__':
    main()
