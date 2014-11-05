from direct.interval.LerpInterval import LerpPosInterval


def animate_model(model, position, duration, callback=None, callback_args=None):
    interval = LerpPosInterval(
        model, duration, position, model.getPos())
    interval.start()

    if callback:
        if not callback_args:
            callback_args = []
        callback(*callback_args)