from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
print(this_directory)
long_description = (this_directory / "README.md").read_text()


setup(
    name='cartesian_viz',
    version='1.0.2',    
    description='Customizable map or cartesian data vizualiser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/androclassic/cartesian_viz',
    author='Andrei Georgescu',
    author_email='andrei.georgescoo@yahoo.com',
    license='MIT License',
    packages=['cartesian_viz'],
    install_requires=[
                        'pyproj>=3.0.1',
                        'scipy>=1.6.2',
                        'scikit-learn==1.0.2',
                        'pandas>=1.0.5',
                        'numpy>=1.26.3', 
                        'gtsam>=4.0.3',                
                      ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
)