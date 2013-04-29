import os
from setuptools import setup, find_packages

version = "1.0"

description = """Tracker for DVS camera"""  # TODO

long_description = description  # TODO

setup(name='aer_tracker',
      url='',
      description=description,
      long_description=long_description,
      package_data={'':['*.*']},
      keywords="",
      license="",

      classifiers=[
        'Development Status :: 4 - Beta',
      ],

      version=version,

      download_url=
        'http://github.com/AndreaCensi/rcl/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[
        'ConfTools>=1.0,<2',
        'PyContracts>=1.2,<2',
        'PyYAML',
        'python-cjson',
        'quickapp'
      ],
      tests_require=['nose>=1.1.2,<2'],
      entry_points={

         'console_scripts': [
            'aer_read_log = aer.programs:aer_read_log_main',
            'aer_video = aer.programs:aer_video_main',
            'aer_simple_stats = aer.programs:aer_simple_stats_main',
            'aer_stats_events = aer.programs:aer_stats_events_main',
            'aer_stats_freq = aer.programs:aer_stats_freq_main',
            'aer_stats_freq_phase = aer.programs:aer_stats_freq_phase_main',
            'aer_blink_detect = aer.programs:aer_blink_detect_main',
            'aer_tracker_plot = aer_led_tracker.programs.plot:aer_tracker_plot_main',
            'aer_resolver_plot = aer_led_tracker.programs:aer_resolver_plot_main',
            'aer_particles_plot = aer_led_tracker.programs:aer_particles_plot_main',
        ]
      }
)

