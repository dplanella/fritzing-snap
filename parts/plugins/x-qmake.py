
import os
import shutil

import snapcraft

class QmakePlugin(snapcraft.BasePlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()
        schema['properties']['configflags'] = {
            'type': 'array',
            'minitems': 1,
            'uniqueItems': True,
            'items': {
                'type': 'string',
            },
            'default': [],
        }

        # Inform Snapcraft of the properties associated with building. If these
        # change in the YAML Snapcraft will consider the build step dirty.
        schema['build-properties'].append('configflags')

        # Add an option to pass the name of the .pro file to be used
        schema['properties']['project-file'] = {type: 'string'}

        return schema

    def __init__(self, name, options, project):
        super().__init__(name, options, project)
        self.build_packages.extend(['qt5-qmake', 'make'])

    def build(self):
        super().build()
#        if os.path.exists(self.builddir):
#            shutil.rmtree(self.builddir)
#        os.mkdir(self.builddir)

#        source_subdir = getattr(self.options, 'source_subdir', None)
#        if source_subdir:
#            sourcedir = os.path.join(self.sourcedir, source_subdir)
#        else:
#            sourcedir = self.sourcedir

        env = self._build_environment()

        # Run qmake to generate a Makefile
        print(env)
        if self.options.project_file is not None:
            print("Running my special mode")
            print(self.options.project_file)
            self.run(['qmake', self.options.project_file], env=env)
        else:
            self.run(['qmake'], env=env)

        # Run make to build the sources
        self.run(['make', '-j{}'.format(self.project.parallel_build_count)], env=env)

        # Now install it
        self.run(['make', 'install', 'INSTALL_ROOT={}'.format(self.installdir), 'DESTDIR=' + self.installdir], env=env)

    def _build_environment(self):
        env = os.environ.copy()
        print()
        env['QT_SELECT'] = '5'
        env['LFLAGS'] = '-L ' +  ' -L'.join(
            ['{0}/lib', '{0}/usr/lib', '{0}/lib/{1}',
             '{0}/usr/lib/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['INCDIRS'] =  ':'.join(
            ['{0}/include', '{0}/usr/include', '{0}/include/{1}',
             '{0}/usr/include/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['CPATH'] = ':'.join(
            ['{0}/include', '{0}/usr/include', '{0}/include/{1}',
             '{0}/usr/include/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['LIBRARY_PATH'] = '$LD_LIBRARY_PATH:' + ':'.join(
            ['{0}/lib', '{0}/usr/lib', '{0}/lib/{1}',
             '{0}/usr/lib/{1}']).format(
                self.project.stage_dir, self.project.arch_triplet)
        env['SNAPPY_BUILD'] = "1"
        return env

