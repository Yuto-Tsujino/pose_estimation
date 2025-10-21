#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include "pybind11/stl.h" // std::vector, std::map のために追加
#include <m3api/xiApi.h>

#include <stdexcept>
#include <string>
#include <vector>
#include <map>
#include <memory> // std::unique_ptr のために追加

namespace py = pybind11;

// エラーチェック用のヘルパー関数
void check_xi_error(XI_RETURN stat, const std::string& func_name) {
    if (stat != XI_OK) {
        throw std::runtime_error("XIMEA API Error in " + func_name + ": " + std::to_string(stat));
    }
}

// 接続されているカメラの識別情報をリストで取得する関数
std::vector<std::map<std::string, std::string>> get_camera_list() {
    DWORD num_devices = 0;
    check_xi_error(xiGetNumberDevices(&num_devices), "xiGetNumberDevices");

    std::vector<std::map<std::string, std::string>> camera_list;
    for (DWORD i = 0; i < num_devices; ++i) {
        // unique_ptrでハンドルを管理し、例外発生時も確実にクローズする
        HANDLE h = nullptr;
        try {
            check_xi_error(xiOpenDevice(i, &h), "xiOpenDevice(index=" + std::to_string(i) + ")");
            
            char sn[256] = {0}, inst_path[256] = {0};
            xiGetParamString(h, XI_PRM_DEVICE_SN, sn, sizeof(sn));
            xiGetParamString(h, XI_PRM_DEVICE_INSTANCE_PATH, inst_path, sizeof(inst_path));
            
            std::map<std::string, std::string> cam_info;
            cam_info["serial_number"] = std::string(sn);
            cam_info["instance_path"] = std::string(inst_path);
            
            camera_list.push_back(cam_info);
            xiCloseDevice(h);
        } catch (...) {
            if (h) xiCloseDevice(h);
            throw; // エラーを再スロー
        }
    }
    return camera_list;
}

class XiCam {
public:
    // コンストラクタ: シリアル番号ではなく instance_path でカメラを開く
    explicit XiCam(const std::string& instance_path) {
        // XI_OPEN_BY_INST_PATH を使って直接デバイスを開く
        XI_RETURN stat = xiOpenDeviceBy(XI_OPEN_BY_INST_PATH, instance_path.c_str(), &xiH);
        if (stat != XI_OK) {
            throw std::runtime_error("Failed to open camera with instance_path: " + instance_path);
        }

        // パラメータ設定
        xiSetParamInt(xiH, XI_PRM_EXPOSURE, 5000);
        xiSetParamInt(xiH, XI_PRM_IMAGE_DATA_FORMAT, XI_RGB24);

        // 撮影開始
        check_xi_error(xiStartAcquisition(xiH), "xiStartAcquisition");
    }

    ~XiCam() {
        if (xiH) {
            xiStopAcquisition(xiH);
            xiCloseDevice(xiH);
        }
    }

    // grab関数は変更なし
    py::array_t<uint8_t> grab() {
        XI_IMG img = {};
        img.size = sizeof(XI_IMG);

        check_xi_error(xiGetImage(xiH, 5000, &img), "xiGetImage");
        
        // img.bp が null でないことを確認
        if (img.bp == nullptr) {
            throw std::runtime_error("Failed to get image data (null buffer).");
        }

        int height = img.height;
        int width = img.width;
        int channels = 3; // XI_RGB24

        // py::capsuleでラップして、元のバッファが解放されないようにする
        // (ここではコピーするので必須ではないが、より安全な実装の参考として)
        // auto capsule = py::capsule(img.bp, [](void *p) { /* 何もしない */ });

        return py::array_t<uint8_t>(
            {height, width, channels},                           // shape
            {width * channels, channels, 1},                     // strides
            static_cast<uint8_t*>(img.bp) // buffer pointer
        ).attr("copy")(); // コピーを作成してバッファの所有権をPythonに移す
    }

private:
    HANDLE xiH = nullptr;
};

PYBIND11_MODULE(ximea_wrap, m) {
    m.doc() = "Python binding for XIMEA xiapi";

    // ヘルパー関数をモジュールに追加
    m.def("get_camera_list", &get_camera_list, "Get a list of connected cameras with their identifiers.");

    // XiCamクラスを定義
    py::class_<XiCam>(m, "XiCam")
        .def(py::init<const std::string&>(), "Initialize and open a camera by its instance_path")
        .def("grab", &XiCam::grab, "Capture an image and return it as a NumPy array");
}