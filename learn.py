from bl_common import get_device, get_packet


def main():

    # initialise variables
    p = ""

    # get broadlink device
    device = get_device()

    while p is not None:

        # get packet
        print("\nPress a button\n")
        p = get_packet(device,5)

        # if no packet received, prompt to try again
        while p is None:
            prompt = None
            
            while prompt not in ['Y','y','N','n']:
                prompt = str(input('Nothing received. Try again?\n(Y/N) '))
            
            if prompt.strip().upper() == 'N':
                break

            print("\nPress a button\n")
            p = get_packet(device,5)

        # break loop if user chooses not to try again
        if p is None:
            break

        # print packet
        print(f'{p}\n')

if __name__ == '__main__':
    main()
