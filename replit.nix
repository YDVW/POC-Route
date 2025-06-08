{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.replitPackages.prybar-python311
    pkgs.replitPackages.stderred
    pkgs.postgresql
    pkgs.openssl
    pkgs.libffi
    pkgs.pkg-config
    pkgs.zlib
    pkgs.libjpeg
    pkgs.freetype
    pkgs.gfortran
    pkgs.blas
    pkgs.lapack
    pkgs.stdenv.cc.cc.lib
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      # Core system libraries
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.openssl
      pkgs.libffi
      # Needed for pandas / numpy
      pkgs.gfortran.cc.lib
      pkgs.blas
      pkgs.lapack
      # Graphics libraries
      pkgs.glib
      pkgs.xorg.libX11
      pkgs.libjpeg
      pkgs.freetype
    ];
    PYTHONHOME = "${pkgs.python311Full}";
    PYTHONBIN = "${pkgs.python311Full}/bin/python3.11";
    LANG = "en_US.UTF-8";
    STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
    PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python311}/bin/prybar-python311";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.openssl
      pkgs.libffi
      pkgs.gfortran.cc.lib
    ];
  };
} 