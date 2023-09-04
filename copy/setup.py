from setuptools import setup, find_packages()

setup(name='clean_folder',
      version='0.0.1',
      description='Clean folder',
      url='http://github.com/dummy_user/useful',
      author='Go It',
      author_email='flyingcircus@example.com',
      license='MIT',
      #packages=find_packages(),
      packages=['clean_folder'],
      entry_points={'console_scripts': ['clean-folder = clean_folder.clean:main']},
)
