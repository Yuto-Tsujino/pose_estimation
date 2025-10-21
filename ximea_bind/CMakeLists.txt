cmake_minimum_required(VERSION 3.22)
project(ximea_bind)

set(CMAKE_CXX_STANDARD 17)

# --- XIMEA SDKのルートディレクトリを指定 ---
# 環境変数を利用するか、直接パスを記述します。
# このCMakeLists.txtから見た相対パスで指定するのが管理しやすいでしょう。
set(XIMEA_PACKAGE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../package)

# --- Pythonとpybind11の設定 ---
find_package(pybind11 REQUIRED)
find_package(PythonLibs 3.10 REQUIRED) # ご利用のPythonバージョンに合わせてください

# --- ヘッダーファイルのインクルードパスを設定 ---
# XIMEAのヘッダーファイルが含まれるディレクトリを追加します。
include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(${XIMEA_PACKAGE_DIR}/include)

# --- ライブラリファイルの検索パスを設定 ---
# .soファイルが含まれるディレクトリを追加します。
# libm3api.so は api/X64 に、libxiapi.so は CamTool.64 にあります。
link_directories(
    ${XIMEA_PACKAGE_DIR}/api/X64
    ${XIMEA_PACKAGE_DIR}/CamTool.64 
    # ↑ XIMEAのドキュメントでは、xiapiの実体はlibm3api.soとして提供されている場合が多いため、
    #   CamTool.64よりもapi/X64が正しい可能性があります。
    #   もしCamTool.64内にlibxiapi.soが存在しない場合は、この行は不要です。
)


# --- Python拡張モジュールをビルド ---
# pybind11_add_moduleを推奨 (find_package(pybind11) が提供する便利な関数)
pybind11_add_module(ximea_wrap MODULE src/ximea_wrap.cpp)

# --- ライブラリをリンク ---
# target_link_librariesでライブラリ名を指定します。
# find_package(pybind11) を使うと ${pybind11_LIBRARIES} 変数も利用できます。
# XIMEAのライブラリは 'm3api' と 'xiapi' をリンクします。
# libm3api.so は 'm3api' と指定します。
# libxiCore.so が xiapi の実体である場合 'xiCore' と指定します。
target_link_libraries(ximea_wrap PRIVATE
    ${PYTHON_LIBRARIES}
    m3api # libm3api.so に対応
    xiCore # libxiCore.so (xiapi本体) に対応
)

# --- 出力ファイル名のプレフィックスを削除 (任意) ---
# Linuxでは通常 'lib' が付きますが、Pythonモジュールとしては不要なため削除します。
set_target_properties(ximea_wrap PROPERTIES PREFIX "")