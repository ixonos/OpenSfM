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

        tol = 0.01
        init_focal = float(args.focal_prior)
        max_iter = 15

        for i in range(max_iter):

            report, reconstructions, zero_pair = reconstruction.incremental_reconstruction_fastrack(data, 
                                                                                     tracks_manager, 
                                                                                     focal_prior=init_focal)
            
            if zero_pair:
                print("calibration failed, no pairs to initialize bundle adjustment")
                break

            rec1 = reconstructions.pop()
            rec1_key = next(iter(rec1.cameras.keys()))
            est_focal = rec1.cameras[rec1_key].focal

            if ((init_focal - est_focal) <= tol):
                print("Tolerance reached. Focal est: ", est_focal, "Iteration: ",i)
                break
            else:
                print("est focal: ", est_focal)
                init_focal = est_focal
                

        # opensfm takes focal length as normalized value relative to max(img_height, img_width)
        # so convert it back to pixels
        camera_priors = data.load_camera_models()
        cam_key = next(iter(camera_priors.keys()))
        img_width = camera_priors[cam_key].width
        img_height = camera_priors[cam_key].height

        scale_factor = max(img_width, img_height)

        with open(data.est_focal_log(), 'a') as fout:
            fout.write(str(est_focal * scale_factor))

        # with open(data.profile_log(), 'a') as fout:
        #     fout.write('reconstruct: {0}\n'.format(end - start))
        # data.save_reconstruction(reconstructions)
        # data.save_report(io.json_dumps(report), 'reconstruction.json')
