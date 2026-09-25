import os
from dotenv import load_dotenv

load_dotenv()

from services.vi_tri_service import ViTriService
from services.khu_vuc_service import KhuVucService
from services.parking_service import ParkingService

def test_services():
    print("Testing ViTriService.get_all()...")
    vitris = ViTriService.get_all()
    print("ViTri count:", len(vitris))
    print("ViTri data:", vitris)

    print("Testing KhuVucService.lay_cho_trong()...")
    cho_trong = KhuVucService.lay_cho_trong()
    print("KhuVuc cho trong:", cho_trong)

    print("Testing ParkingService.get_status()...")
    status = ParkingService.get_status()
    print("Parking status:", status)

if __name__ == "__main__":
    test_services()
