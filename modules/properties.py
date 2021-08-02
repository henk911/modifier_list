import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import PropertyGroup

from . import modifier_categories
from .utils import get_ml_active_object


# Callbacks
# ======================================================================

def modifier_active_index_get(self):
    ob = get_ml_active_object()

    for mod in ob.modifiers:
        if mod.is_active:
            return ob.modifiers.find(mod.name)

    return 0


def modifier_active_index_set(self, value):
    mods = get_ml_active_object().modifiers

    if mods:
        mods[value].is_active = True


def pinned_object_ensure_users(scene):
    """Handler for making sure a pinned object which is only used by
    pinned_object, i.e. an object which was deleted while it was
    pinned, really gets deleted + the property gets reset.
    """
    ml_props = scene.modifier_list

    if ml_props.pinned_object:
        if ml_props.pinned_object.users == 1 and not ml_props.pinned_object.use_fake_user:
            bpy.data.objects.remove(ml_props.pinned_object)
            ml_props.pinned_object = None


def on_pinned_object_change(self, context):
    """Callback function for pinned_object"""
    depsgraph_handlers = bpy.app.handlers.depsgraph_update_pre

    if context.scene.modifier_list.pinned_object:
        depsgraph_handlers.append(pinned_object_ensure_users)
    else:
        try:
            depsgraph_handlers.remove(pinned_object_ensure_users)
        except ValueError:
            pass


def set_all_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    all_modifiers = bpy.context.window_manager.modifier_list.all_modifiers
    sorted_names_icons_types = sorted(modifier_categories.ALL_MODIFIERS_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not all_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = all_modifiers.add()
            item.name = name
            item.value = mod


def set_mesh_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    mesh_modifiers = bpy.context.window_manager.modifier_list.mesh_modifiers
    sorted_names_icons_types = sorted(modifier_categories.MESH_ALL_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not mesh_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = mesh_modifiers.add()
            item.name = name
            item.value = mod


def set_curve_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    curve_modifiers = bpy.context.window_manager.modifier_list.curve_modifiers
    sorted_names_icons_types = sorted(modifier_categories.CURVE_ALL_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not curve_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = curve_modifiers.add()
            item.name = name
            item.value = mod


def set_lattice_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    lattice_modifiers = bpy.context.window_manager.modifier_list.lattice_modifiers
    sorted_names_icons_types = sorted(modifier_categories.LATTICE_ALL_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not lattice_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = lattice_modifiers.add()
            item.name = name
            item.value = mod


def set_pointcloud_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    pointcloud_modifiers = bpy.context.window_manager.modifier_list.pointcloud_modifiers
    sorted_names_icons_types = sorted(modifier_categories.POINTCLOUD_ALL_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not pointcloud_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = pointcloud_modifiers.add()
            item.name = name
            item.value = mod


def set_volume_modifier_collection_items():
    """This is to be called on loading a new file or reloading addons
    to make modifiers available in search.
    """
    volume_modifiers = bpy.context.window_manager.modifier_list.volume_modifiers
    sorted_names_icons_types = sorted(modifier_categories.VOLUME_ALL_NAMES_ICONS_TYPES,
                                      key=lambda mod: mod[0])

    if not volume_modifiers:
        for name, _, mod in sorted_names_icons_types:
            item = volume_modifiers.add()
            item.name = name
            item.value = mod


@persistent
def on_file_load(dummy):
    set_all_modifier_collection_items()
    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()
    set_pointcloud_modifier_collection_items()
    set_volume_modifier_collection_items()


def add_modifier(self, context):
    # Add modifier
    ml_props = bpy.context.window_manager.modifier_list
    mod_name = ml_props.modifier_to_add_from_search

    if mod_name == "":
        return None

    mod_type = ml_props.all_modifiers[mod_name].value
    bpy.ops.object.ml_modifier_add(modifier_type=mod_type)

    # Executing an operator via a function doesn't create an undo event,
    # so it needs to be added manually.
    bpy.ops.ed.undo_push(message="Add Modifier")


# Modifier collections
# ======================================================================

class AllModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class MeshModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class CurveModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class LatticeModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class PointcloudModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


class VolumeModifiersCollection(PropertyGroup):
    # Collection Property for search
    value: StringProperty(name="Type")


# Property groups
# ======================================================================

class ML_SceneProperties(PropertyGroup):
    pinned_object: PointerProperty(
        type=bpy.types.Object,
        update=on_pinned_object_change)


class ML_PreferencesUIProperties(PropertyGroup):
    favourite_modifiers_expand: BoolProperty(name="", default=True)
    favourite_modifiers_menu_expand: BoolProperty(name="", default=True)
    general_expand: BoolProperty(name="")
    popup_expand: BoolProperty(name="")
    gizmo_expand: BoolProperty(name="")
    modifier_defaults_expand: BoolProperty()
    modifier_to_show_defaults_for: StringProperty(
        name="Modifier to show defaults for",
        description="Search for a modifier to show its customizable default settings",
        default="Armature")


class ML_WindowManagerProperties(PropertyGroup):
    modifier_to_add_from_search: StringProperty(
        name="Modifier to add",
        update=add_modifier,
        description="Search for a modifier and add it to the stack")
    all_modifiers: CollectionProperty(type=AllModifiersCollection)
    mesh_modifiers: CollectionProperty(type=MeshModifiersCollection)
    curve_modifiers: CollectionProperty(type=CurveModifiersCollection)
    lattice_modifiers: CollectionProperty(type=LatticeModifiersCollection)
    pointcloud_modifiers: CollectionProperty(type=PointcloudModifiersCollection)
    volume_modifiers: CollectionProperty(type=VolumeModifiersCollection)
    popup_tabs_items = [
        ("MODIFIERS", "Modifiers", "Modifiers", 'MODIFIER', 1),
        ("OBJECT_DATA", "Object Data", "Object Data", 'MESH_DATA', 2),
    ]
    popup_active_tab: EnumProperty(
        items=popup_tabs_items,
        name="Popup Tabs",
        default='MODIFIERS')
    preferences_ui_props: PointerProperty(type=ML_PreferencesUIProperties)
    active_favourite_modifier_slot_index: IntProperty()
    gizmo_object_settings_expand: BoolProperty()


# Registering
# ======================================================================

classes = (
    AllModifiersCollection,
    MeshModifiersCollection,
    CurveModifiersCollection,
    LatticeModifiersCollection,
    PointcloudModifiersCollection,
    VolumeModifiersCollection,
    ML_SceneProperties,
    ML_PreferencesUIProperties,
    ML_WindowManagerProperties
)


def register():
    # === Properties ===
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.ml_modifier_active_index = IntProperty(
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        get=modifier_active_index_get,
        set=modifier_active_index_set)

    wm = bpy.types.WindowManager
    wm.modifier_list = PointerProperty(type=ML_WindowManagerProperties)

    bpy.types.Scene.modifier_list = PointerProperty(type=ML_SceneProperties)

    bpy.app.handlers.load_post.append(on_file_load)

    set_all_modifier_collection_items()
    set_mesh_modifier_collection_items()
    set_curve_modifier_collection_items()
    set_lattice_modifier_collection_items()
    set_pointcloud_modifier_collection_items()
    set_volume_modifier_collection_items()


def unregister():
    bpy.app.handlers.load_post.remove(on_file_load)

    del bpy.types.Object.ml_modifier_active_index
    del bpy.types.WindowManager.modifier_list
    del bpy.types.Scene.modifier_list

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
