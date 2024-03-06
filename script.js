//Test
function submitVote(chosenCharacterId, otherCharacterId) {
    document.getElementById('chosenCharacter').value = chosenCharacterId;
    document.getElementById('otherCharacter').value = otherCharacterId;
    document.getElementById('characterForm').submit();
}