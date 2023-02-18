import CapImg from '../assets/images/Cap.png';
import CascadeImg from '../assets/images/Cascade.png';
import SandImg from '../assets/images/Sand.png';
import LakeImg from '../assets/images/Lake.png';
import WoodedImg from '../assets/images/Wooded.png';
import LostImg from '../assets/images/Lost.png';
import MetroImg from '../assets/images/Metro.png';
import SnowImg from '../assets/images/Snow.png';
import SeasideImg from '../assets/images/Seaside.png';
import LuncheonImg from '../assets/images/Luncheon.png';
import BowsersImg from '../assets/images/Bowsers.png';
import MoonImg from '../assets/images/Moon.png';
import MushroomImg from '../assets/images/Mushroom.png';

export const kingdomImages = {
  Cap: CapImg,
  Cascade: CascadeImg,
  Sand: SandImg,
  Lake: LakeImg,
  Wooded: WoodedImg,
  Lost: LostImg,
  Metro: MetroImg,
  Snow: SnowImg,
  Seaside: SeasideImg,
  Luncheon: LuncheonImg,
  Bowsers: BowsersImg,
  Moon: MoonImg,
  Mushroom: MushroomImg,
};

export const mainGameKingdoms = [
  'Cascade',
  'Sand',
  'Wooded',
  'Lake',
  'Lost',
  'Metro',
  'Snow',
  'Seaside',
  'Luncheon',
  'Bowsers',
];

export const availableKingdoms = ['Cap', ...mainGameKingdoms, 'Moon', 'Mushroom'];
