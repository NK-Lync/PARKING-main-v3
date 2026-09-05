
from datetime import datetime

from database.supabase_client import supabase


class ParkingService:

    # ============================================================
    # XE VÀO BÃI
    # ============================================================
    @staticmethod
    def vehicle_entry(bien_so, ma_loai_xe):

        # --------------------------------------------------------
        # 1. Kiểm tra xe đã có lượt gửi đang hoạt động chưa
        # --------------------------------------------------------
        active_vehicle = (
            supabase
            .table("luotguixe")
            .select("*")
            .eq("bienso", bien_so)
            .eq("tinhtrang", "Đang gửi")
            .execute()
        )

        if active_vehicle.data:
            return {
                "success": False,
                "message": "Xe này đang ở trong bãi"
            }

        # --------------------------------------------------------
        # 2. Kiểm tra loại xe có tồn tại không
        # --------------------------------------------------------
        vehicle_type = (
            supabase
            .table("loaixe")
            .select("*")
            .eq("maloaixe", ma_loai_xe)
            .execute()
        )

        if not vehicle_type.data:
            return {
                "success": False,
                "message": "Không tìm thấy loại xe"
            }

        # --------------------------------------------------------
        # 3. Lấy toàn bộ vị trí
        # --------------------------------------------------------
        positions_response = (
            supabase
            .table("vitrido")
            .select("*")
            .order("mavitri")
            .execute()
        )

        positions = positions_response.data

        if not positions:
            return {
                "success": False,
                "message": "Bãi xe chưa có vị trí đỗ"
            }

        # --------------------------------------------------------
        # 4. Lấy toàn bộ vị trí đang có xe active
        # --------------------------------------------------------
        active_parkings_response = (
            supabase
            .table("luotguixe")
            .select("mavitri")
            .eq("tinhtrang", "Đang gửi")
            .execute()
        )

        active_parkings = (
            active_parkings_response.data or []
        )

        occupied_position_ids = {
            parking["mavitri"]
            for parking in active_parkings
            if parking.get("mavitri") is not None
        }

        # --------------------------------------------------------
        # 5. Tìm vị trí thực sự trống
        # --------------------------------------------------------
        available_position = None

        for position in positions:

            position_id = position["mavitri"]

            is_marked_empty = (
                position["trangthai"] == "Còn trống"
            )

            is_used_by_active_vehicle = (
                position_id in occupied_position_ids
            )

            if (
                is_marked_empty
                and not is_used_by_active_vehicle
            ):
                available_position = position
                break

        # --------------------------------------------------------
        # 6. Không còn vị trí hợp lệ
        # --------------------------------------------------------
        if available_position is None:
            return {
                "success": False,
                "message": "Bãi xe đã đầy"
            }

        position_id = available_position["mavitri"]

        # --------------------------------------------------------
        # 7. Thời gian vào
        # --------------------------------------------------------
        now = datetime.now()

        # --------------------------------------------------------
        # 8. Tạo lượt gửi xe
        # --------------------------------------------------------
        parking_data = {
            "bienso": bien_so,
            "maloaixe": ma_loai_xe,
            "mavitri": position_id,
            "thoigianvao": now.isoformat(),
            "tongphi": 0,
            "tinhtrang": "Đang gửi"
        }

        try:

            parking_response = (
                supabase
                .table("luotguixe")
                .insert(parking_data)
                .execute()
            )

        except Exception as e:

            error_message = str(e)

            if (
                "unique_active_parking_position"
                in error_message
            ):
                return {
                    "success": False,
                    "message": (
                        "Vị trí vừa được xe khác sử dụng. "
                        "Vui lòng thử lại"
                    )
                }

            return {
                "success": False,
                "message": error_message
            }

        if not parking_response.data:
            return {
                "success": False,
                "message": "Không thể tạo lượt gửi xe"
            }

        # --------------------------------------------------------
        # 9. Cập nhật vị trí thành đang sử dụng
        # --------------------------------------------------------
        position_update = (
            supabase
            .table("vitrido")
            .update({
                "trangthai": "Đang sử dụng"
            })
            .eq("mavitri", position_id)
            .execute()
        )

        # --------------------------------------------------------
        # 10. Kiểm tra việc cập nhật vị trí
        # --------------------------------------------------------
        if not position_update.data:
            return {
                "success": False,
                "message": (
                    "Đã tạo lượt gửi nhưng không thể "
                    "cập nhật trạng thái vị trí"
                ),
                "data": {
                    "luotgui": parking_response.data[0]
                }
            }

        # --------------------------------------------------------
        # 11. Trả kết quả
        # --------------------------------------------------------
        return {
            "success": True,
            "message": "Xe vào bãi thành công",
            "data": {
                "luotgui": parking_response.data[0],
                "vitri": {
                    **available_position,
                    "trangthai": "Đang sử dụng"
                }
            }
        }


    # ============================================================
    # XE VÀO BÃI TẠI VỊ TRÍ AI XÁC ĐỊNH
    # ============================================================
    @staticmethod
    def vehicle_entry_at_position(
        bien_so,
        ma_loai_xe,
        ma_vi_tri
    ):
        """
        Tạo lượt gửi xe tại đúng vị trí mà AI xác định.

        Luồng:

            Camera
                ↓
            AI nhận diện xe
                ↓
            AI nhận diện biển số
                ↓
            AI xác định vị trí
                ↓
            vehicle_entry_at_position()

        Khác với vehicle_entry():

            vehicle_entry()
                → tự tìm vị trí trống.

            vehicle_entry_at_position()
                → sử dụng đúng vị trí do AI xác định.
        """

        # --------------------------------------------------------
        # 1. Kiểm tra dữ liệu đầu vào
        # --------------------------------------------------------
        if not bien_so:
            return {
                "success": False,
                "message": "Thiếu biển số xe"
            }

        if ma_loai_xe is None:
            return {
                "success": False,
                "message": "Thiếu mã loại xe"
            }

        if ma_vi_tri is None:
            return {
                "success": False,
                "message": "Thiếu mã vị trí"
            }

        bien_so = bien_so.strip().upper()

        # --------------------------------------------------------
        # 2. Kiểm tra xe đã có lượt gửi active chưa
        # --------------------------------------------------------
        active_vehicle = (
            supabase
            .table("luotguixe")
            .select(
                "maluotgui, bienso, maloaixe, mavitri, "
                "thoigianvao, thoigianra, tongphi, tinhtrang"
            )
            .eq("bienso", bien_so)
            .eq("tinhtrang", "Đang gửi")
            .limit(1)
            .execute()
        )

        if active_vehicle.data:
            return {
                "success": False,
                "message": "Xe này đang ở trong bãi",
                "data": {
                    "luotgui": active_vehicle.data[0]
                }
            }

        # --------------------------------------------------------
        # 3. Kiểm tra loại xe
        # --------------------------------------------------------
        vehicle_type = (
            supabase
            .table("loaixe")
            .select(
                "maloaixe, tenloaixe, dongia"
            )
            .eq("maloaixe", ma_loai_xe)
            .limit(1)
            .execute()
        )

        if not vehicle_type.data:
            return {
                "success": False,
                "message": "Không tìm thấy loại xe"
            }

        # --------------------------------------------------------
        # 4. Kiểm tra vị trí có tồn tại không
        # --------------------------------------------------------
        position_response = (
            supabase
            .table("vitrido")
            .select(
                "mavitri, tenkhuvuc, trangthai"
            )
            .eq("mavitri", ma_vi_tri)
            .limit(1)
            .execute()
        )

        if not position_response.data:
            return {
                "success": False,
                "message": "Vị trí đỗ không tồn tại"
            }

        position = position_response.data[0]

        # --------------------------------------------------------
        # 5. Kiểm tra vị trí đã có xe active chưa
        # --------------------------------------------------------
        active_position = (
            supabase
            .table("luotguixe")
            .select(
                "maluotgui, bienso, mavitri, tinhtrang"
            )
            .eq("mavitri", ma_vi_tri)
            .eq("tinhtrang", "Đang gửi")
            .limit(1)
            .execute()
        )

        if active_position.data:
            return {
                "success": False,
                "message": "Vị trí này đang có xe",
                "data": {
                    "vitri": position,
                    "luotgui": active_position.data[0]
                }
            }

        # --------------------------------------------------------
        # 6. Kiểm tra trạng thái vị trí
        # --------------------------------------------------------
        if position["trangthai"] != "Còn trống":
            return {
                "success": False,
                "message": (
                    "Vị trí không ở trạng thái còn trống"
                ),
                "data": {
                    "vitri": position
                }
            }

        # --------------------------------------------------------
        # 7. Tạo lượt gửi xe
        # --------------------------------------------------------
        now = datetime.now()

        parking_data = {
            "bienso": bien_so,
            "maloaixe": ma_loai_xe,
            "mavitri": ma_vi_tri,
            "thoigianvao": now.isoformat(),
            "thoigianra": None,
            "tongphi": 0,
            "tinhtrang": "Đang gửi"
        }

        try:

            parking_response = (
                supabase
                .table("luotguixe")
                .insert(parking_data)
                .execute()
            )

        except Exception as e:

            error_message = str(e)

            if (
                "unique_active_parking_position"
                in error_message
            ):
                return {
                    "success": False,
                    "message": (
                        "Vị trí vừa được xe khác sử dụng. "
                        "Vui lòng thử lại"
                    )
                }

            return {
                "success": False,
                "message": error_message
            }

        if not parking_response.data:
            return {
                "success": False,
                "message": "Không thể tạo lượt gửi xe"
            }

        created_parking = parking_response.data[0]

        # --------------------------------------------------------
        # 8. Cập nhật vị trí
        # --------------------------------------------------------
        position_update = (
            supabase
            .table("vitrido")
            .update({
                "trangthai": "Đang sử dụng"
            })
            .eq("mavitri", ma_vi_tri)
            .execute()
        )

        # --------------------------------------------------------
        # 9. Nếu cập nhật vị trí thất bại → rollback
        # --------------------------------------------------------
        if not position_update.data:

            (
                supabase
                .table("luotguixe")
                .delete()
                .eq(
                    "maluotgui",
                    created_parking["maluotgui"]
                )
                .execute()
            )

            return {
                "success": False,
                "message": (
                    "Không thể cập nhật trạng thái vị trí"
                )
            }

        # --------------------------------------------------------
        # 10. Trả kết quả
        # --------------------------------------------------------
        return {
            "success": True,
            "message": (
                "Xe vào bãi thành công tại "
                "vị trí AI xác định"
            ),
            "data": {
                "luotgui": created_parking,
                "vitri": position_update.data[0],
                "nguon": "AI"
            }
        }


    # ============================================================
    # XE RA KHỎI BÃI
    # ============================================================
    @staticmethod
    def vehicle_exit(bien_so):

        # --------------------------------------------------------
        # 1. Tìm lượt gửi đang hoạt động
        # --------------------------------------------------------
        active_vehicle = (
            supabase
            .table("luotguixe")
            .select("*")
            .eq("bienso", bien_so)
            .eq("tinhtrang", "Đang gửi")
            .execute()
        )

        if not active_vehicle.data:
            return {
                "success": False,
                "message": (
                    "Không tìm thấy xe đang gửi trong bãi"
                )
            }

        parking = active_vehicle.data[0]

        # --------------------------------------------------------
        # 2. Thời gian ra
        # --------------------------------------------------------
        now = datetime.now()

        # --------------------------------------------------------
        # 3. Chuyển thời gian vào thành datetime
        # --------------------------------------------------------
        time_in = datetime.fromisoformat(
            parking["thoigianvao"].replace(
                "Z",
                "+00:00"
            )
        )

        if time_in.tzinfo is not None:
            time_in = time_in.replace(
                tzinfo=None
            )

        # --------------------------------------------------------
        # 4. Tính thời gian gửi
        # --------------------------------------------------------
        duration = now - time_in

        total_seconds = (
            duration.total_seconds()
        )

        total_minutes = max(
            1,
            int(total_seconds / 60)
        )

        # Làm tròn lên số giờ
        total_hours = max(
            1,
            int(
                (total_minutes + 59) / 60
            )
        )

        # --------------------------------------------------------
        # 5. Kiểm tra vé tháng
        # --------------------------------------------------------
        monthly_pass = (
            supabase
            .table("vethang")
            .select("*")
            .eq("bienso", bien_so)
            .eq("trangthai", True)
            .execute()
        )

        has_valid_monthly_pass = False

        if monthly_pass.data:

            for ticket in monthly_pass.data:

                expiry = datetime.fromisoformat(
                    ticket["ngayhethan"]
                    .replace(
                        "Z",
                        "+00:00"
                    )
                )

                if expiry.tzinfo is not None:
                    expiry = expiry.replace(
                        tzinfo=None
                    )

                if expiry >= now:
                    has_valid_monthly_pass = True
                    break

        # --------------------------------------------------------
        # 6. Tính phí
        # --------------------------------------------------------
        total_fee = 0

        if not has_valid_monthly_pass:

            vehicle_type = (
                supabase
                .table("loaixe")
                .select("*")
                .eq(
                    "maloaixe",
                    parking["maloaixe"]
                )
                .execute()
            )

            if not vehicle_type.data:
                return {
                    "success": False,
                    "message": "Không tìm thấy loại xe"
                }

            price_per_hour = (
                vehicle_type.data[0]["dongia"]
            )

            total_fee = (
                total_hours * price_per_hour
            )

        # --------------------------------------------------------
        # 7. Cập nhật lượt gửi thành Đã trả
        # --------------------------------------------------------
        updated_parking = (
            supabase
            .table("luotguixe")
            .update({
                "thoigianra": now.isoformat(),
                "tongphi": total_fee,
                "tinhtrang": "Đã trả"
            })
            .eq(
                "maluotgui",
                parking["maluotgui"]
            )
            .execute()
        )

        if not updated_parking.data:
            return {
                "success": False,
                "message": (
                    "Không thể cập nhật lượt gửi xe"
                )
            }

        # --------------------------------------------------------
        # 8. Kiểm tra xem vị trí còn xe active khác không
        # --------------------------------------------------------
        other_active_vehicle = (
            supabase
            .table("luotguixe")
            .select(
                "maluotgui, bienso, mavitri"
            )
            .eq(
                "mavitri",
                parking["mavitri"]
            )
            .eq(
                "tinhtrang",
                "Đang gửi"
            )
            .neq(
                "maluotgui",
                parking["maluotgui"]
            )
            .execute()
        )

        # --------------------------------------------------------
        # 9. Chỉ giải phóng vị trí nếu KHÔNG còn xe active
        # --------------------------------------------------------
        if not other_active_vehicle.data:

            (
                supabase
                .table("vitrido")
                .update({
                    "trangthai": "Còn trống"
                })
                .eq(
                    "mavitri",
                    parking["mavitri"]
                )
                .execute()
            )

        else:

            (
                supabase
                .table("vitrido")
                .update({
                    "trangthai": "Đang sử dụng"
                })
                .eq(
                    "mavitri",
                    parking["mavitri"]
                )
                .execute()
            )

        # --------------------------------------------------------
        # 10. Trả kết quả
        # --------------------------------------------------------
        return {
            "success": True,
            "message": "Xe ra khỏi bãi thành công",
            "data": {
                "bienso": bien_so,
                "thoigianvao":
                    parking["thoigianvao"],
                "thoigianra":
                    now.isoformat(),
                "thoigian_gui_phut":
                    total_minutes,
                "so_gio_tinh_phi":
                    total_hours,
                "co_ve_thang":
                    has_valid_monthly_pass,
                "tongphi":
                    total_fee,
                "maluotgui":
                    parking["maluotgui"],
                "mavitri":
                    parking["mavitri"],
                "luotgui":
                    updated_parking.data
            }
        }


    # ============================================================
    # ĐỒNG BỘ AI → SUPABASE
    # ============================================================
    @staticmethod
    def sync_ai_occupancy(ai_result):
        """
        Đồng bộ trạng thái vị trí từ AI xuống bảng vitrido.

        AI chỉ cung cấp trạng thái quan sát.

        AI KHÔNG:
        - tạo LuotGuiXe
        - đóng LuotGuiXe
        - tính phí
        - tự xác định xe vào/ra

        LuotGuiXe vẫn là dữ liệu nghiệp vụ chính.

        Phân loại kết quả đồng bộ:

        updated:
            AI làm thay đổi trạng thái Supabase.

        overridden:
            AI nói "Còn trống" nhưng LuotGuiXe
            đang có xe active tại vị trí đó.
            Hệ thống giữ "Đang sử dụng".

        unchanged:
            Trạng thái AI giống trạng thái Supabase
            và không cần thay đổi.

        failed:
            Không tìm thấy vị trí hoặc cập nhật thất bại.
        """

        # --------------------------------------------------------
        # 1. Kiểm tra kết quả AI
        # --------------------------------------------------------
        if not ai_result:
            return {
                "success": False,
                "message": "Không có kết quả AI"
            }

        if not ai_result.get("success"):
            return {
                "success": False,
                "message": "Kết quả AI không hợp lệ"
            }

        ai_data = ai_result.get("data")

        if not ai_data:
            return {
                "success": False,
                "message": "Thiếu dữ liệu AI"
            }

        ai_slots = ai_data.get("vi_tri")

        if not ai_slots:
            return {
                "success": False,
                "message":
                    "AI không trả về danh sách vị trí"
            }

        # --------------------------------------------------------
        # 2. Lấy toàn bộ vị trí hiện tại từ Supabase
        # --------------------------------------------------------
        positions_response = (
            supabase
            .table("vitrido")
            .select(
                "mavitri, tenkhuvuc, trangthai"
            )
            .order("mavitri")
            .execute()
        )

        positions = (
            positions_response.data or []
        )

        # Tạo dictionary để tra cứu nhanh:
        # {
        #     1: {...},
        #     2: {...},
        #     ...
        # }
        positions_by_id = {
            position["mavitri"]: position
            for position in positions
            if position.get("mavitri") is not None
        }

        # --------------------------------------------------------
        # 3. Lấy các lượt gửi đang active
        #
        # Đây là dữ liệu nghiệp vụ đáng tin cậy.
        # --------------------------------------------------------
        active_parkings_response = (
            supabase
            .table("luotguixe")
            .select(
                "maluotgui, bienso, mavitri"
            )
            .eq(
                "tinhtrang",
                "Đang gửi"
            )
            .execute()
        )

        active_parkings = (
            active_parkings_response.data or []
        )

        active_position_ids = {
            parking["mavitri"]
            for parking in active_parkings
            if parking.get("mavitri") is not None
        }

        # --------------------------------------------------------
        # 4. Các nhóm kết quả
        # --------------------------------------------------------
        updated_slots = []
        overridden_slots = []
        unchanged_slots = []
        failed_slots = []

        # --------------------------------------------------------
        # 5. Đồng bộ từng vị trí AI
        # --------------------------------------------------------
        for slot in ai_slots:

            ma_vi_tri = slot.get("mavitri")
            ai_status = slot.get("trangthai")

            # ----------------------------------------------------
            # 5.1. Kiểm tra mã vị trí
            # ----------------------------------------------------
            if ma_vi_tri is None:

                failed_slots.append({
                    "reason": "Thiếu mavitri",
                    "slot": slot
                })

                continue

            # ----------------------------------------------------
            # 5.2. Kiểm tra trạng thái AI
            # ----------------------------------------------------
            if ai_status not in [
                "Còn trống",
                "Đang sử dụng"
            ]:

                failed_slots.append({
                    "mavitri": ma_vi_tri,
                    "ai_trangthai": ai_status,
                    "reason":
                        "Trạng thái AI không hợp lệ"
                })

                continue

            # ----------------------------------------------------
            # 5.3. Kiểm tra vị trí có tồn tại trong DB
            # ----------------------------------------------------
            current_position = (
                positions_by_id.get(ma_vi_tri)
            )

            if current_position is None:

                failed_slots.append({
                    "mavitri": ma_vi_tri,
                    "ai_trangthai": ai_status,
                    "reason":
                        "Vị trí không tồn tại trong Supabase"
                })

                continue

            current_status = (
                current_position["trangthai"]
            )

            # ----------------------------------------------------
            # 5.4. Bảo vệ dữ liệu nghiệp vụ
            #
            # Nếu LuotGuiXe đang có xe tại vị trí này
            # nhưng AI lại nói "Còn trống",
            # không cho AI giải phóng vị trí.
            # ----------------------------------------------------
            if (
                ma_vi_tri in active_position_ids
                and
                ai_status == "Còn trống"
            ):

                final_status = "Đang sử dụng"

                # Nếu DB đã là "Đang sử dụng"
                # thì chỉ ghi nhận là unchanged.
                if current_status == final_status:

                    unchanged_slots.append({
                        "mavitri": ma_vi_tri,
                        "ai_trangthai": ai_status,
                        "trangthai_supabase":
                            current_status,
                        "reason":
                            "Đang có LuotGuiXe active"
                    })

                else:

                    # Trường hợp DB đang sai trạng thái,
                    # cần sửa lại thành "Đang sử dụng".
                    update_response = (
                        supabase
                        .table("vitrido")
                        .update({
                            "trangthai": final_status
                        })
                        .eq(
                            "mavitri",
                            ma_vi_tri
                        )
                        .execute()
                    )

                    if update_response.data:

                        overridden_slots.append({
                            "mavitri": ma_vi_tri,
                            "ai_trangthai": ai_status,
                            "trangthai_cu":
                                current_status,
                            "trangthai_cuoi":
                                final_status,
                            "reason":
                                "Đang có LuotGuiXe active"
                        })

                    else:

                        failed_slots.append({
                            "mavitri": ma_vi_tri,
                            "ai_trangthai": ai_status,
                            "reason":
                                "Không thể cập nhật "
                                "trạng thái bảo vệ nghiệp vụ"
                        })

                continue

            # ----------------------------------------------------
            # 5.5. Nếu trạng thái DB đã giống AI
            # ----------------------------------------------------
            if current_status == ai_status:

                unchanged_slots.append({
                    "mavitri": ma_vi_tri,
                    "ai_trangthai": ai_status,
                    "trangthai_supabase":
                        current_status
                })

                continue

            # ----------------------------------------------------
            # 5.6. AI thực sự làm thay đổi trạng thái DB
            # ----------------------------------------------------
            update_response = (
                supabase
                .table("vitrido")
                .update({
                    "trangthai": ai_status
                })
                .eq(
                    "mavitri",
                    ma_vi_tri
                )
                .execute()
            )

            if update_response.data:

                updated_slots.append({
                    "mavitri": ma_vi_tri,
                    "ai_trangthai": ai_status,
                    "trangthai_cu":
                        current_status,
                    "trangthai_moi":
                        ai_status
                })

            else:

                failed_slots.append({
                    "mavitri": ma_vi_tri,
                    "ai_trangthai": ai_status,
                    "trangthai_cu":
                        current_status,
                    "reason":
                        "Không thể cập nhật vị trí"
                })

        # --------------------------------------------------------
        # 6. Tổng hợp kết quả
        # --------------------------------------------------------
        total_processed = (
            len(updated_slots)
            +
            len(overridden_slots)
            +
            len(unchanged_slots)
            +
            len(failed_slots)
        )

        # --------------------------------------------------------
        # 7. Trả kết quả
        # --------------------------------------------------------
        return {
            "success": True,
            "message":
                "Đồng bộ AI → Supabase thành công",
            "data": {

                "tong_so_vi_tri_ai":
                    len(ai_slots),

                "tong_so_vi_tri_xu_ly":
                    total_processed,

                "so_vi_tri_cap_nhat":
                    len(updated_slots),

                "so_vi_tri_bao_ve_nghiep_vu":
                    len(overridden_slots),

                "so_vi_tri_khong_doi":
                    len(unchanged_slots),

                "so_vi_tri_loi":
                    len(failed_slots),

                "vi_tri_da_cap_nhat":
                    updated_slots,

                "vi_tri_bi_ghi_de_boi_nghiep_vu":
                    overridden_slots,

                "vi_tri_khong_doi":
                    unchanged_slots,

                "vi_tri_loi":
                    failed_slots
            }
        }


    # ============================================================
    # TRẠNG THÁI BÃI XE
    # ============================================================
    @staticmethod
    def get_status():

        # --------------------------------------------------------
        # 1. Lấy toàn bộ vị trí
        # --------------------------------------------------------
        positions_response = (
            supabase
            .table("vitrido")
            .select("*")
            .order("mavitri")
            .execute()
        )

        positions = (
            positions_response.data or []
        )

        total_positions = len(
            positions
        )

        # --------------------------------------------------------
        # 2. Lấy toàn bộ lượt gửi đang active
        # --------------------------------------------------------
        parking_response = (
            supabase
            .table("luotguixe")
            .select("*")
            .eq(
                "tinhtrang",
                "Đang gửi"
            )
            .order("maluotgui")
            .execute()
        )

        active_parkings = (
            parking_response.data or []
        )

        # --------------------------------------------------------
        # 3. Tập hợp các vị trí thực sự đang có xe
        # --------------------------------------------------------
        active_position_ids = {
            parking["mavitri"]
            for parking in active_parkings
            if parking.get("mavitri") is not None
        }

        # --------------------------------------------------------
        # 4. Số vị trí thực sự đang sử dụng
        #
        # Dựa trên LuotGuiXe active.
        # --------------------------------------------------------
        occupied_positions = len(
            active_position_ids
        )

        occupied_positions = min(
            occupied_positions,
            total_positions
        )

        # --------------------------------------------------------
        # 5. Số vị trí còn trống
        # --------------------------------------------------------
        empty_positions = (
            total_positions
            -
            occupied_positions
        )

        # --------------------------------------------------------
        # 6. Tỷ lệ lấp đầy
        # --------------------------------------------------------
        occupancy_rate = 0

        if total_positions > 0:

            occupancy_rate = round(
                occupied_positions
                /
                total_positions
                *
                100,
                2
            )

        # --------------------------------------------------------
        # 7. Tạo danh sách xe đang gửi
        # --------------------------------------------------------
        vehicles = []

        for parking in active_parkings:

            position = next(
                (
                    p
                    for p in positions
                    if p["mavitri"]
                    == parking["mavitri"]
                ),
                None
            )

            vehicles.append({
                "maluotgui":
                    parking["maluotgui"],

                "bienso":
                    parking["bienso"],

                "maloaixe":
                    parking["maloaixe"],

                "mavitri":
                    parking["mavitri"],

                "tenkhuvuc":
                    (
                        position["tenkhuvuc"]
                        if position
                        else None
                    ),

                "thoigianvao":
                    parking["thoigianvao"],

                "tinhtrang":
                    parking["tinhtrang"]
            })

        # --------------------------------------------------------
        # 8. Trả kết quả
        # --------------------------------------------------------
        return {
            "success": True,
            "message":
                "Lấy trạng thái bãi xe thành công",
            "data": {

                "tong_vi_tri":
                    total_positions,

                "dang_su_dung":
                    occupied_positions,

                "con_trong":
                    empty_positions,

                "ty_le_lap_day":
                    occupancy_rate,

                "xe_dang_gui":
                    vehicles
            }
        }
