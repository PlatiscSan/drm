from ruamel.yaml import YAML
from mp_api.client import MPRester
from pymatgen.io.cif import CifWriter
import os

excluded_set = set([
	# toxic elements
	"Hg", "Cd", "As",
	# radioactive elements
	"Tc", "Pm", "Po", "At", "Rn", "Fr", 
	"Ra", "Ac", "Th", "Pa", "U" , "Np", 
	"Pu", "Am", "Cm", "Bk", "Cf", "Es", 
	"Fm", "Md", "No", "Lr", "Rf", "Db", 
	"Sg", "Bh", "Hs", "Mt", "Ds", "Rg", 
	"Cn", "Nh", "Fl", "Mc", "Lv", "Ts", 
	"Og"
])

with open("../conf/materials_project.yaml", "r") as f:
	try:
		materials_project_conf = YAML().load(f)
	except FileNotFoundError:
		print("../conf/materials_project.yaml not found. Please create the file with your Materials Project API key.")
		materials_project_conf = {}
	except Exception as e:
		print(f"Error loading materials_project.yaml: {e}")
		materials_project_conf = {}

if "api_key" not in materials_project_conf:
	print("Configuration missing 'api_key'. Exiting.")
	exit(1)

api_key = materials_project_conf["api_key"]

print(f"Using Materials Project API key: {api_key}")

with MPRester(api_key) as mpr:
	try:
		docs = mpr.materials.summary.search(
			elements=["Ni"], # TODO: should be loaded from config
			band_gap=(0, 0.5),
			efermi=(0, 2.5),
			is_stable=True,
			formation_energy=(-3, 0.5)
		)
		docs = list(
			filter(lambda doc: not excluded_set.intersection(doc.elements), docs)
		)
		print(f"Found {len(docs)} requested compounds.")
		try:
			os.makedirs("../cifs", exist_ok=True)
		except Exception as e:
			print(f"Error occurred while creating cifs directory: {e}")
			exit(1)
		for doc in docs:
			material_id = doc.material_id
			try:
				structure = mpr.get_structure_by_material_id(material_id)
				filename = f"../cifs/{material_id}.cif"
				CifWriter(structure).write_file(filename)
				print(f"Downloaded: {filename}")
			except Exception as e:
				print(f"Failed to download {material_id}: {e}")
	except Exception as e:
		print(f"Error occurred while initializing MPRester: {e}")

print("Finished downloading CIF files.")