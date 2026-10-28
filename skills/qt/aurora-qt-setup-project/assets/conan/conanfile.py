from conan import ConanFile


class Application(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "PkgConfigDeps"

    # Declare the application's Aurora Conan package references here.
    # Also review CMake pkg-config linking and RPM bundled-library requirements.
    requires = ()
