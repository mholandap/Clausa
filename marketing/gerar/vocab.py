_pad="$"; _punct=';:,.!?¡¿—…"«»“” '
_letters='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
_ipa="ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ"
SYM=[_pad]+list(_punct)+list(_letters)+list(_ipa)
V={s:i for i,s in enumerate(SYM)}
# Kokoro v1.0: '«»' viraram '()' e letras maiúsculas usadas são deslocadas; para pt usamos só minúsculas/IPA.
V['(']=12; V[')']=13; V['̃']=17
for k in list(V):
    if k.isupper() and k.isascii(): del V[k]
