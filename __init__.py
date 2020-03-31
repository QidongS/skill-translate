from opsdroid.skill import Skill
from opsdroid.matchers import match_regex
import aiohttp
import execjs

languages = {
  "af": "Afrikaans",
  "sq": "Albanian",
  "ar": "Arabic",
  "az": "Azerbaijani",
  "eu": "Basque",
  "bn": "Bengali",
  "be": "Belarusian",
  "bg": "Bulgarian",
  "ca": "Catalan",
  "zh-CN": "Simplified Chinese",
  "zh-TW": "Traditional Chinese",
  "hr": "Croatian",
  "cs": "Czech",
  "da": "Danish",
  "nl": "Dutch",
  "en": "English",
  "eo": "Esperanto",
  "et": "Estonian",
  "tl": "Filipino",
  "fi": "Finnish",
  "fr": "French",
  "gl": "Galician",
  "ka": "Georgian",
  "de": "German",
  "el": "Greek",
  "gu": "Gujarati",
  "ht": "Haitian Creole",
  "iw": "Hebrew",
  "hi": "Hindi",
  "hu": "Hungarian",
  "is": "Icelandic",
  "id": "Indonesian",
  "ga": "Irish",
  "it": "Italian",
  "ja": "Japanese",
  "kn": "Kannada",
  "ko": "Korean",
  "la": "Latin",
  "lv": "Latvian",
  "lt": "Lithuanian",
  "mk": "Macedonian",
  "ms": "Malay",
  "mt": "Maltese",
  "no": "Norwegian",
  "fa": "Persian",
  "pl": "Polish",
  "pt": "Portuguese",
  "ro": "Romanian",
  "ru": "Russian",
  "sr": "Serbian",
  "sk": "Slovak",
  "sl": "Slovenian",
  "es": "Spanish",
  "sw": "Swahili",
  "sv": "Swedish",
  "ta": "Tamil",
  "te": "Telugu",
  "th": "Thai",
  "tr": "Turkish",
  "uk": "Ukrainian",
  "ur": "Urdu",
  "vi": "Vietnamese",
  "cy": "Welsh",
  "yi": "Yiddish"}

# references https://github.com/cocoa520/Google_TK
class Py4Js():
  def __init__(self):
    self.ctx = execjs.compile("""
      function TL(a) {
      var k = "";
      var b = 406644;
      var b1 = 3293161072;

      var jd = ".";
      var $b = "+-a^+6";
      var Zb = "+-3^+b+-f";

      for (var e = [], f = 0, g = 0; g < a.length; g++) {
          var m = a.charCodeAt(g);
          128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
          e[f++] = m >> 18 | 240,
          e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
          e[f++] = m >> 6 & 63 | 128),
          e[f++] = m & 63 | 128)
      }
      a = b;
      for (f = 0; f < e.length; f++) a += e[f],
      a = RL(a, $b);
      a = RL(a, Zb);
      a ^= b1 || 0;
      0 > a && (a = (a & 2147483647) + 2147483648);
      a %= 1E6;
      return a.toString() + jd + (a ^ b)
  };

  function RL(a, b) {
      var t = "a";
      var Yb = "+";
      for (var c = 0; c < b.length - 2; c += 3) {
          var d = b.charAt(c + 2),
          d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
          d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
          a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
      }
      return a
  }
  """)

  def getTk(self, text):
    return self.ctx.call("TL", text)

class TSkill(Skill):
  async def translate(self, text, sl, tl):
    js = Py4Js()
    tk = js.getTk(text)
    param = {'tk': tk, 'q': text}
    url = "https://translate.google.com/translate_a/single?"
    query = "client=t&sl={}&tl={}&hl=en&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1&srcrom=0&ssel=0&tsel=0&kc=2".format(sl, tl)
    async with aiohttp.ClientSession() as session:
      async with session.get(url+query, params=param) as resp:
        return await resp.json()


  @match_regex(r"translate (.*) from (.*) to (.*)", case_sensitive=False)
  async def show_translation(self, message):
    text = message.regex.group(1)
    from_language = message.regex.group(2)
    to_language = message.regex.group(3)
    sl = None
    tl =None
    for code, lang in languages.items():
      if lang.lower() == from_language:
        sl = code
      if lang.lower() == to_language:
        tl = code
    if sl == tl:
      return await message.respond("Same Language")
    if sl is None or tl is None:
      return await message.respond("No such languages")
    result = await self.translate(text, sl, tl)
    if result is None or result[0] is None:
      return await message.respond("error")
    word = result[0][0][0]
    return await message.respond("{} is {} in {}".format(text, word, to_language))

