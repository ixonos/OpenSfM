import logging

from opensfm import dataset
from opensfm import io
from opensfm import reconstruction

logger = logging.getLogger(__name__)

def reconstruct(data_path, focal_prior = 1.0):

    data = dataset.DataSet(data_path)
    tracks_manager = data.load_tracks_manager()

    tol = 0.01
    init_focal = 0.85
    est_focal = focal_prior
    max_iter = 15

    logger.info("content of data_path: %s", data_path)

    for i in range(max_iter):

        report, reconstructions, zero_pair = reconstruction.incremental_reconstruction_fastrack(data, 
                                                                                    tracks_manager, 
                                                                                    focal_prior=init_focal)
        
        if zero_pair:
            logger.info("Unable to initialize bundle adjustment... exiting")
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

    return est_focal * scale_factor

    # with open(data.est_focal_log(), 'a') as fout:
    #     fout.write(str(est_focal * scale_factor))

    # with open(data.profile_log(), 'a') as fout:
    #     fout.write('reconstruct: {0}\n'.format(end - start))
    # data.save_reconstruction(reconstructions)
    # data.save_report(io.json_dumps(report), 'reconstruction.json')
