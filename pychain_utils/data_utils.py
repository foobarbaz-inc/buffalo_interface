import random
import json
import numpy as np
from PIL import Image
import io

from pychain_utils.bundlr import upload_data

def torch_img_to_arweave(img_tensor):
    # tensor is a [B, C, H, W] tensor scaled to [0, 1)
    img = img_tensor.clamp(0, 1).detach().cpu().numpy()
    img = (img*255).transpose(1, 2, 0).astype(np.uint8)
    img = Image.fromarray(img)
    output_bytes = io.BytesIO()
    img.save(output_bytes, format='JPEG', quality=95)
    output_location = upload_data(output_bytes.getvalue())
    return output_location

def convert_to_NFT(arweave_path, seed, description):
    json_data = {
        'name': random_title(seed),
        'description': description,
        'external_url': 'https://buffalolabs.xyz/',
        'image': arweave_path,
    }
    json_data_bytes = json.dumps(json_data, indent=4, sort_keys=True).encode()
    output_location = upload_data(json_data_bytes)
    return output_location

nouns = ["Dream","Dreamer","Dreams","Waves",
"Sword","Kiss","Sex","Lover",
"Slave","Slaves","Pleasure","Servant",
"Servants","Snake","Soul","Touch",
"Men","Women","Gift","Scent",
"Ice","Snow","Night","Silk","Secret","Secrets",
"Game","Fire","Flame","Flames",
"Husband","Wife","Man","Woman","Boy","Girl",
"Truth","Edge","Boyfriend","Girlfriend",
"Body","Captive","Male","Wave","Predator",
"Female","Healer","Trainer","Teacher",
"Hunter","Obsession","Hustler","Consort",
"Dream", "Dreamer", "Dreams","Rainbow",
"Dreaming","Flight","Flying","Soaring",
"Wings","Mist","Sky","Wind",
"Winter","Misty","River","Door",
"Gate","Cloud","Fairy","Dragon",
"End","Blade","Beginning","Tale",
"Tales","Emperor","Prince","Princess",
"Willow","Birch","Petals","Destiny",
"Theft","Thief","Legend","Prophecy",
"Spark","Sparks","Stream","Streams","Waves",
"Sword","Darkness","Swords","Silence","Kiss",
"Butterfly","Shadow","Ring","Rings","Emerald",
"Storm","Storms","Mists","World","Worlds",
"Alien","Lord","Lords","Ship","Ships","Star",
"Stars","Force","Visions","Vision","Magic",
"Wizards","Wizard","Heart","Heat","Twins",
"Twilight","Moon","Moons","Planet","Shores",
"Pirates","Courage","Time","Academy",
"School","Rose","Roses","Stone","Stones",
"Sorcerer","Shard","Shards","Slave","Slaves",
"Servant","Servants","Serpent","Serpents",
"Snake","Soul","Souls","Savior","Spirit",
"Spirits","Voyage","Voyages","Voyager","Voyagers",
"Return","Legacy","Birth","Healer","Healing",
"Year","Years","Death","Dying","Luck","Elves",
"Tears","Touch","Son","Sons","Child","Children",
"Illusion","Sliver","Destruction","Crying","Weeping",
"Gift","Word","Words","Thought","Thoughts","Scent",
"Ice","Snow","Night","Silk","Guardian","Angel",
"Angels","Secret","Secrets","Search","Eye","Eyes",
"Danger","Game","Fire","Flame","Flames","Bride",
"Husband","Wife","Time","Flower","Flowers",
"Light","Lights","Door","Doors","Window","Windows",
"Bridge","Bridges","Ashes","Memory","Thorn",
"Thorns","Name","Names","Future","Past",
"History","Something","Nothing","Someone",
"Nobody","Person","Man","Woman","Boy","Girl",
"Way","Mage","Witch","Witches","Lover",
"Tower","Valley","Abyss","Hunter",
"Truth","Edge"]

adjectives = ["Lost","Only","Last","First",
"Third","Sacred","Bold","Lovely",
"Final","Missing","Shadowy","Seventh",
"Dwindling","Missing","Absent",
"Vacant","Cold","Hot","Burning","Forgotten",
"Weeping","Dying","Lonely","Silent",
"Laughing","Whispering","Forgotten","Smooth",
"Silken","Rough","Frozen","Wild",
"Trembling","Fallen","Ragged","Broken",
"Cracked","Splintered","Slithering","Silky",
"Wet","Magnificent","Luscious","Swollen",
"Erect","Bare","Naked","Stripped",
"Captured","Stolen","Sucking","Licking",
"Growing","Kissing","Green","Red","Blue",
"Azure","Rising","Falling","Elemental",
"Bound","Prized","Obsessed","Unwilling",
"Hard","Eager","Ravaged","Sleeping",
"Wanton","Professional","Willing","Devoted",
"Misty","Lost","Only","Last","First",
"Final","Missing","Shadowy","Seventh",
"Dark","Darkest","Silver","Silvery","Living",
"Black","White","Hidden","Entwined","Invisible",
"Next","Seventh","Red","Green","Blue",
"Purple","Grey","Bloody","Emerald","Diamond",
"Frozen","Sharp","Delicious","Dangerous",
"Deep","Twinkling","Dwindling","Missing","Absent",
"Vacant","Cold","Hot","Burning","Forgotten",
"Some","No","All","Every","Each","Which","What",
"Playful","Silent","Weeping","Dying","Lonely","Silent",
"Laughing","Whispering","Forgotten","Smooth","Silken",
"Rough","Frozen","Wild","Trembling","Fallen",
"Ragged","Broken","Cracked","Splintered"]

def random_title(seed):
    random.seed(seed)

    noun1 = random.choice(nouns)
    noun2 = random.choice(nouns)
    adj = random.choice(adjectives)
    titles = [
        f'{adj} {noun1}',
        f'The {adj} {noun1}',
        f'{noun1} of {noun2}',
        f'The {noun1}\'s {noun2}',
        f'The {noun1} of the {noun2}',
        f'{noun1} in the {noun2}'
    ]
    title = random.choice(titles)
    return title
