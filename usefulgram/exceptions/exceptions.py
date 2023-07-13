

NoOneButtonParamIsFilled = ValueError("No one button parameters is filled")

DifferentButtonsInMatrix = ValueError("Only one type of button is allowed in the markup")

UnknownButtonType = ValueError("UnknownButtonType")

TooMoreCharacters = ValueError("The callback data can be only 64 bytes"
                               "(~62 or less characters because separator)")

RecursionObjectParse = ValueError("Now objects cannot contain objects")
