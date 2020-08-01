import logging
import time

from opensfm import dataset
from opensfm import io
from opensfm import reconstruction

logger = logging.getLogger(__name__)


class Command:
    name = 'reconstruct'
    help = "Compute the reconstruction"

    def add_arguments(self, parser):
        parser.add_argument('dataset', help='dataset to process')
        parser.add_argument('focal_prior', default=0.9, help='initial focal length for BA')

    def run(self, args):
        start = time.time()
        data = dataset.DataSet(args.dataset)
        tracks_manager = data.load_tracks_manager()

        # report, reconstructions = reconstruction.\
        #     incremental_reconstruction(data, tracks_manager)

        report, reconstructions, zero_pairs = reconstruction.\
            incremental_reconstruction_fastrack(data, tracks_manager, float(args.focal_prior))

        if zero_pairs:
            print("calibration faild, no pairs to initialize bundle adjustment")

        camera_priors = data.load_camera_models()
        for i in camera_priors.keys():
            img_width = camera_priors[i].width

        rec1 = reconstructions.pop()
        for i in rec1.cameras.keys():
            est_focal = rec1.cameras[i].focal

        end = time.time()

        with open(data.est_focal_log(), 'a') as fout:
            fout.write(str(est_focal * img_width))

        # with open(data.profile_log(), 'a') as fout:
        #     fout.write('reconstruct: {0}\n'.format(end - start))
        # data.save_reconstruction(reconstructions)
        # data.save_report(io.json_dumps(report), 'reconstruction.json')
