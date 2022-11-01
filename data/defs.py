from performance_event_repo import PerformanceEventRepo
import os

encoder = PerformanceEventRepo(steps_per_second=100, num_velocity_bins=32,
                               stretch_factors='1.0',
                               pitch_transpose_lower=-3,
                               pitch_transpose_upper=-3)

def run_from_text(path, out_dir):
    filename, extension = os.path.splitext(os.path.basename(path))
    encoder.from_text(path, os.path.join(out_dir, filename + '.mid'))